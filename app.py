import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import RegistrationForm, LoginForm, SellBooksForm, EditProfileForm
from sqlcon import connect
import random
from functools import wraps
import bcrypt
from datetime import date

app = Flask(__name__)
app.secret_key = "bookmart"

conn = connect()


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first!','info')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
@login_required
def home():
    books = f'SELECT * FROM `books` WHERE 1'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(books)
    all_books = cursor.fetchall()
    return render_template('index.html', books=all_books)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        user_id = "U" + str(random.randint(100, 999)) + str(random.randint(100, 999)) + str(random.randint(100, 999))
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password").encode('utf-8')
        hashed=bcrypt.hashpw(password,bcrypt.gensalt()).decode()
        date_joined = str(date.today())
        new_user = f'INSERT INTO `users`(`user_id`,`name`, `email`, `password`,`date_joined`) VALUES ("{user_id}","{name}", "{email}", "{hashed}","{date_joined}")'
        cursor = conn.cursor()
        cursor.execute(new_user)
        conn.commit()
        flash('Signed up Successfully! Proceed to Login.','success')
        return redirect(url_for('login'))
    return render_template('signup.html', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password").encode('utf-8')
        login = f'SELECT `user_id`, `name`, `email`, `password` FROM `users` WHERE `email` LIKE "{email}" '
        cursor = conn.cursor()
        cursor.execute(login)
        user = cursor.fetchall()
        if len(user) > 0:
            if bcrypt.checkpw(password,user[0][3].encode('utf-8')):
                session['logged_in']=True
                session['id']=user[0][0]
                session['name']=user[0][1]
                flash('Logged in Successfully!','success')
                return redirect(url_for('home'))
            else:
                flash('Email address and Password did not match','danger')
        else:
            flash('Email address does not exist','danger')
        return redirect(url_for('login'))
    return render_template('login.html', form = form)


def save_picture(form_image):
    img_id = "I" + str(random.randint(100, 999)) + str(random.randint(100, 999)) + str(random.randint(100, 999))
    _, f_ext = os.path.splitext(form_image.filename)
    pic_fn = img_id + f_ext
    pic_path = os.path.join('static/book_images', pic_fn)
    form_image.save(pic_path)
    return pic_fn


@app.route('/sell_books', methods=['GET', 'POST'])
@login_required
def sell_books():
    form = SellBooksForm()
    if request.method == 'POST' and form.validate_on_submit():
        book_id = "B" + str(random.randint(100, 999)) + str(random.randint(100, 999)) + str(random.randint(100, 999))
        book_name = request.form.get("book_name")
        book_author = request.form.get("author_name")
        publication = request.form.get("publication_name")
        branch_id = request.form.get("branch")
        book_edition = request.form.get("edition")
        isbn = request.form.get("isbn")
        condition = request.form.get("book_condition")
        cond_dict = {'Fine/Like New': 0.10, 'Good': 0.20, 'Fair': 0.30, 'Poor': 0.40}
        book_oprice = float(request.form.get("price"))
        book_dprice = book_oprice - book_oprice*float(cond_dict[condition])
        book_image = save_picture(form.image.data)
        date_added = str(date.today())
        new_book = f'INSERT INTO `books`(`book_id`, `book_name`, `book_author`, `publication_name`,`branch_id`, `edition`, `isbn`, `book_condition`, `price`, `discounted_price`, `image_id`, `date_added`) VALUES ("{book_id}","{book_name}","{book_author}","{publication}", {branch_id}, {book_edition}, "{isbn}", "{condition}", {book_oprice}, {book_dprice}, "{book_image}", "{date_added}")'
        cursor = conn.cursor()
        cursor.execute(new_book)
        conn.commit()
        flash('Book added!', 'success')
        return redirect(url_for('sell_books'))  
    return render_template('sellbooks.html', book_form=form)
 
@app.route('/search',methods=['GET','POST'])
@login_required
def search():
    book_name = request.form.get("book_name")
    #book = request.form['book']
    cursor = conn.cursor()
    book_search=f'SELECT `book_name` from `books` WHERE `book_name`  LIKE "{book_name}"'
    cursor.execute(book_search)
    conn.commit()
    data = cursor.fetchall()
    return render_template('base.html', data=data)
    
@app.route('/profile')
@login_required
def profile():
    userid = session['id']
    user = f'SELECT `user_id`, `name`, `email`, `password` FROM `users` WHERE `user_id` = "{userid}" '
    cursor = conn.cursor(dictionary=True)
    cursor.execute(user)
    user = cursor.fetchone()
    return render_template('profile.html', user=user)

@app.route('/edit_profile')
@login_required
def edit_profile():
    edit_form = EditProfileForm()
    userid = session['id']
    user = f'SELECT `user_id`, `name`, `email`, `password` FROM `users` WHERE `user_id` = "{userid}" '
    cursor = conn.cursor()
    cursor.execute(user)
    user = cursor.fetchone()
    if request.method == 'GET':
        edit_form.name.data = user[1]
        edit_form.email.data = user[2]
    return render_template('edit_profile.html', edit_form=edit_form)

@app.route('/bought_books')
@login_required
def bought_books():
    return render_template('boughtbooks.html')

@app.route('/sold_books')
@login_required
def sold_books():
    return render_template('soldbooks.html')

@app.route('/view/<book_id>/')
@login_required
def view(book_id):
    book = f'SELECT * FROM `books` WHERE book_id={book_id}'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(book)
    curr_book = cursor.fetchone()
    return render_template('view.html', book=curr_book)


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    flash('Logged out Successfully!','warning')
    session.pop('logged_in')
    session.pop('id')
    session.pop('name')
    return redirect(url_for('login'))



if __name__ == '__main__':
   app.run(debug=True)