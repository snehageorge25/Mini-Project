from flask import Flask, render_template, request, redirect, url_for
from sqlcon import connect

app = Flask(__name__)
app.secret_key = "bookmart"

conn = connect()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    return render_template('adminlogin.html')

@app.route('/sell_books')
def sell_books():
    return render_template('sellbooks.html')

@app.route('/edit_profile')
def edit_profile():
    return render_template('edit_profile.html')

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    name = request.form.get("n_name")
    email = request.form.get("n_email")
    password = request.form.get("n_password")
    print(request.form)
    new_user = f'INSERT INTO `users`(`name`, `email`, `password`) VALUES ("{name}", "{email}", "{password}")'
    print(new_user)
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
        return redirect(url_for('home'))


if __name__ == '__main__':
   app.run(debug=True)