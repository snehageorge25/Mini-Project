from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/admin_login')
def admin_login():
    return render_template('adminlogin.html')

@app.route('/sell_books')
def sell_books():
    return render_template('sellbooks.html')

if __name__ == '__main__':
   app.run(debug=True)