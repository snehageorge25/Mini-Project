from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import RegistrationForm, LoginForm, SellBooksForm, EditProfileForm
from sqlcon import connect
import bcrypt
from datetime import date

app = Flask(__name__)
app.secret_key = "bookmart"

conn = connect()

@app.route('/')
def home():
    if 'id' in session:
        flash('Logged in Successfully!','success')
        books = f'SELECT * FROM `books` WHERE 1'
        cursor = conn.cursor(dictionary=True)
        cursor.execute(books)
        all_books = cursor.fetchall()
        return render_template('index.html', books=all_books)
    else:
        return redirect(url_for('login'))    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password").encode('utf-8')
        hashed=bcrypt.hashpw(password,bcrypt.gensalt()).decode()
        date_joined = str(date.today())
        new_user = f'INSERT INTO `users`(`name`, `email`, `pw`,`date_joined`) VALUES ("{name}", "{email}", "{hashed}","{date_joined}")'
        cursor = conn.cursor()
        cursor.execute(new_user)
        conn.commit()
        flash('Signed up Successfully! Proceed to Login.','success')
        return redirect(url_for('login'))
    return render_template('signup.html', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form = form)
    
@app.route('/sell_books')
def sell_books():
    form = SellBooksForm()
    return render_template('sellbooks.html', book_form=form)

@app.route('/profile')
def profile():
    userid = session['id']
    user = f'SELECT `id`, `name`, `email`, `pw` FROM `users` WHERE `id` = {userid} '
    cursor = conn.cursor(dictionary=True)
    cursor.execute(user)
    user = cursor.fetchone()
    return render_template('profile.html', user=user)

@app.route('/edit_profile')
def edit_profile():
    edit_form = EditProfileForm()
    userid = session['id']
    user = f'SELECT `id`, `name`, `email`, `pw` FROM `users` WHERE `id` = {userid} '
    cursor = conn.cursor()
    cursor.execute(user)
    user = cursor.fetchone()
    if request.method == 'GET':
        edit_form.name.data = user[1]
        edit_form.email.data = user[2]
    return render_template('edit_profile.html', edit_form=edit_form)

@app.route('/bought_books')
def bought_books():
    return render_template('boughtbooks.html')

@app.route('/sold_books')
def sold_books():
    return render_template('soldbooks.html')

@app.route('/view/<book_id>/')
def view(book_id):
    book = f'SELECT * FROM `books` WHERE book_id={book_id}'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(book)
    curr_book = cursor.fetchone()
    return render_template('view.html', book=curr_book)


@app.route('/login_validation', methods=['GET', 'POST'])
def login_validation():
    email = request.form.get("email")
    password = request.form.get("password").encode('utf-8')
    login = f'SELECT `id`, `name`, `email`, `pw` FROM `users` WHERE `email` LIKE "{email}" '
    cursor = conn.cursor()
    cursor.execute(login)
    user = cursor.fetchall()
    if len(user) > 0:
        if bcrypt.checkpw(password,user[0][3].encode('utf-8')):
            session['id']=user[0][0]
            session['name']=user[0][1] 
            return redirect(url_for('home'))
        else:
            flash('Email address and Password did not match','danger')
    else:
        flash('Email address does not exist','danger')
    return redirect(url_for('login'))

@app.route('/logout', methods=['GET','POST'])
def logout():
    flash('Logged out Successfully!','warning')
    session.pop('id')
    session.pop('name')
    return redirect(url_for('login'))


@app.route('/new_book', methods=['GET','POST'])
def new_book():
    book_name = request.form.get("BookName")
    book_author = request.form.get("AuthorName")
    publication = request.form.get("Publication")
    book_edition = request.form.get("Edition")
    book_oprice = request.form.get("Price")
    new_book = f'INSERT INTO `books`(`book_name`, `book_author`, `publication`, `book_edition`, `book_oprice`) VALUES ("{book_name}","{book_author}","{publication}",{book_edition},{book_oprice})'
    cursor = conn.cursor()
    cursor.execute(new_book)
    conn.commit()
    return redirect(url_for('sell_books'))



if __name__ == '__main__':
   app.run(debug=True)