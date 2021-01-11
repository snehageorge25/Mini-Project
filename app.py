import os
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import RegistrationForm, LoginForm, SellBooksForm, EditProfileForm, ProfilePicForm
from sqlcon import connect
import random
from functools import wraps
import bcrypt
from datetime import date

app = Flask(__name__)
app.secret_key = "bookmart"

conn = connect()


# inject current user to template context
@app.context_processor
def utility_processor():
    if 'logged_in' in session:
        user_id = session['id']
        user = f'SELECT `user_id`, `name`, `email`, `dob`, `mobile_no`, `addr1`, `addr2`, `pin_code`, `profilepic_id`, `profile_completed` FROM `users` WHERE `user_id` = "{user_id}" '
        cursor = conn.cursor(dictionary=True)
        cursor.execute(user)
        user = cursor.fetchone()
        return dict(user=user)
    else:
        return {'user':'not_logged_in'}


# decorator to check whether user is logged in 
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
        email_exists=f'SELECT * FROM `users` WHERE `email` = "{ email }"'
        cursor = conn.cursor(buffered=True)
        cursor.execute(email_exists)
        if cursor.rowcount==1:
            flash('Email already exists!Please try a different one.','danger')
        else:    
            new_user = f'INSERT INTO `users`(`user_id`,`name`, `email`, `password`,`date_joined`) VALUES ("{user_id}","{name}", "{email}", "{hashed}","{date_joined}")'
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
        cursor = conn.cursor(dictionary=True)
        cursor.execute(login)
        user = cursor.fetchone()
        if user:
            if bcrypt.checkpw(password,user['password'].encode('utf-8')):
                session['logged_in']=True
                session['id']=user['user_id']
                flash('Logged in Successfully!','success')
                return redirect(url_for('home'))
            else:
                flash('Email address and Password did not match','danger')
        else:
            flash('Email address does not exist','danger')
        return redirect(url_for('login'))
    return render_template('login.html', form = form)


def save_picture(form_image, type):
    img_id = type + str(random.randint(100, 999)) + str(random.randint(100, 999)) + str(random.randint(100, 999))
    _, f_ext = os.path.splitext(form_image.filename)
    pic_fn = img_id + f_ext
    if type == "P":
        pic_path = os.path.join('static/profile_pics', pic_fn)
        output_size = (200,200)
        i = Image.open(form_image)
        i.thumbnail(output_size)
        i.save(pic_path)
    else:
        pic_path = os.path.join('static/book_images', pic_fn)
        form_image.save(pic_path)
    return pic_fn


@app.route('/sell_books', methods=['GET', 'POST'])
@login_required
def sell_books():
    form = SellBooksForm()
    user_dict = utility_processor()
    user = user_dict['user']
    if user['profile_completed'] == 1:
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
            book_image = save_picture(form.image.data, "I")
            date_added = str(date.today())
            new_book = f'INSERT INTO `books`(`book_id`, `book_name`, `book_author`, `publication_name`,`branch_id`, `edition`, `isbn`, `book_condition`, `price`, `discounted_price`, `image_id`, `date_added`) VALUES ("{book_id}","{book_name}","{book_author}","{publication}", {branch_id}, {book_edition}, "{isbn}", "{condition}", {book_oprice}, {book_dprice}, "{book_image}", "{date_added}")'
            user_id = session['id']
            new_seller = f'INSERT INTO `sellers`(`seller_id`, `book_id`) VALUES ("{user_id}","{book_id}")'
            cursor = conn.cursor()
            cursor.execute(new_book)
            cursor.execute(new_seller)
            conn.commit()
            flash('Book added!', 'success')
            return redirect(url_for('sell_books'))
    else:
        flash('Complete your profile to proceed', 'warning')
        return redirect(url_for('edit_profile'))
    return render_template('sellbooks.html', book_form=form)


@app.route('/search')
def search():
    book_name = request.args.get("book_name")
    book_search = f'SELECT * from `books` WHERE `book_name` LIKE "%{book_name}%"'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(book_search)
    searched_books = cursor.fetchall()
    return render_template('search.html', books=searched_books)


@app.route('/categories/<branch_name>/')
@login_required
def categories(branch_name):
    branchbooksearch = f'SELECT * FROM `books` WHERE `branch_id` IN (SELECT `branch_id` FROM `branch` WHERE `branch_name`="{branch_name}")'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(branchbooksearch)
    branchbooks = cursor.fetchall()
    return render_template('index.html', books=branchbooks, branch=branch_name)


@app.route('/profile',  methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfilePicForm()
    if request.method == 'POST' and form.validate_on_submit():
        profilepic = save_picture(form.picture.data, "P")
        user_dict = utility_processor()
        user = user_dict['user']
        user_id = user['user_id']
        profilepic_query = f'UPDATE `users` SET `profilepic_id`="{profilepic}" WHERE `user_id`="{user_id}"'
        if user['profilepic_id'] != 'default.jpg':
            remove_profile = 'static/profile_pics/' + user['profilepic_id']
            os.remove(remove_profile)
        cursor = conn.cursor()
        cursor.execute(profilepic_query)
        conn.commit()
        flash('Profile Picture Uploaded!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)

@app.route('/edit_profile',  methods=['GET', 'POST'])
@login_required
def edit_profile():
    edit_form = EditProfileForm()
    user_dict = utility_processor()
    user = user_dict['user']
    user_id = user['user_id']
    if request.method == 'POST' and edit_form.validate_on_submit():
        name = edit_form.name.data
        email = edit_form.email.data
        dob = edit_form.dateofbirth.data
        mobile_no = edit_form.mobileno.data
        addr1 = edit_form.addressline1.data
        addr2 = edit_form.addressline2.data
        pincode = edit_form.pincode.data
        user_info = f'UPDATE `users` SET `name`="{name}", `email`="{email}", `dob`="{dob}", `mobile_no`={mobile_no}, `addr1`="{addr1}", `addr2`="{addr2}", `pin_code`="{pincode}", `profile_completed`=1 WHERE `user_id`="{user_id}"'
        cursor = conn.cursor()
        cursor.execute(user_info)
        conn.commit()
        flash('Profile Completed!', 'success')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        edit_form.name.data = user['name']
        edit_form.email.data = user['email']
        if user['profile_completed'] == 1:
            edit_form.mobileno.data = user['mobile_no']
            edit_form.addressline1.data = user['addr1']
            edit_form.addressline2.data = user['addr2']
            edit_form.pincode.data = user['pin_code']
    return render_template('edit_profile.html', edit_form=edit_form)

@app.route('/bought_books')
@login_required
def bought_books():
    return render_template('boughtbooks.html')

@app.route('/sold_books')
@login_required
def sold_books():
    user_dict = utility_processor()
    user = user_dict['user']
    user_id = user['user_id']
    sold_books = f'SELECT * FROM `books` WHERE `book_id` IN (SELECT `book_id` FROM `sellers` WHERE `seller_id`="{user_id}")'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sold_books)
    books = cursor.fetchall()
    return render_template('soldbooks.html', books=books)

@app.route('/view/<book_id>/')
@login_required
def view(book_id):
    print(book_id)
    book = f'SELECT * FROM `books` WHERE `book_id`="{book_id}"'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(book)
    curr_book = cursor.fetchone()
    return render_template('view.html', book=curr_book)


@app.route('/addbook_to_cart/<book_id>/')
@login_required
def addbook_to_cart(book_id):
    if 'cart' in session:
        cart_list = session['cart']
        cart_list.append(book_id)
        cart_list = list(set(cart_list))
        session['cart'] = cart_list
    else:
        cart_list = [book_id]
        session['cart'] = cart_list
    flash('Book added to cart!', 'success')
    return redirect(url_for('view', book_id=book_id))

    
@app.route('/cart')
@login_required
def cart():
    cart = session['cart']
    cart_string = "'"+ "','".join(cart) + "'"
    cart_query = f'SELECT * FROM `books` WHERE `book_id` IN ({cart_string})'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(cart_query)
    books = cursor.fetchall()
    return render_template('cart.html', books=books)


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    flash('Logged out Successfully!','warning')
    session.pop('logged_in')
    session.pop('id')
    session.pop('cart')
    return redirect(url_for('login'))



if __name__ == '__main__':
   app.run(debug=True)