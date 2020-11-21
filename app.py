from flask import Flask, render_template, request, redirect, url_for,session,flash
from forms import RegistrationForm, LoginForm, SellBooksForm
from sqlcon import connect

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
    return render_template('signup.html', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form = form)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    return render_template('adminlogin.html', form = form)

@app.route('/sell_books')
def sell_books():
    form = SellBooksForm()
    return render_template('sellbooks.html', book_form=form)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/edit_profile')
def edit_profile():
    return render_template('edit_profile.html')

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

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    name = request.form.get("n_name")
    email = request.form.get("n_email")
    password = request.form.get("n_password")
    new_user = f'INSERT INTO `users`(`name`, `email`, `password`) VALUES ("{name}", "{email}", "{password}")'
    cursor = conn.cursor()
    cursor.execute(new_user)
    conn.commit()
    return redirect(url_for('login'))


@app.route('/login_validation', methods=['GET', 'POST'])
def login_validation():
    email = request.form.get("email")
    password = request.form.get("password")
    login = f'SELECT `id`, `name`, `email`, `password` FROM `users` WHERE `email` LIKE "{email}" and `password` LIKE "{password}" '
    cursor = conn.cursor()
    cursor.execute(login)
    users = cursor.fetchall()
    if len(users) > 0:
        session['id']=users[0][0]
        session['name']=users[0][1] 
        return redirect(url_for('home'))
    else:
        flash('Email address and Password did not match.','danger')
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