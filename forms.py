from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, RadioField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message="Name Required"), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    # confirm_password = PasswordField('n_confirm_password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message="Email is required!")])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class SellBooksForm(FlaskForm):
    book_name = StringField('Book Name:', validators=[InputRequired(), Length(min=2, max=100)])
    author_name = StringField('Author Name:', validators=[InputRequired(), Length(min=2, max=100)])
    publication_name = StringField('Publication Name:', validators=[InputRequired(), Length(min=2, max=100)])
    branchchoices = [(1, 'Computer'), (2, 'Information Technology'), (3, 'EnTC'), (4, 'Mechanical') ,(5, 'Civil'), (6, 'Electrical')]
    branch = SelectField('Branch Name:',choices=branchchoices, validators=[InputRequired()])
    edition = IntegerField('Edition:', validators=[InputRequired(), NumberRange(min=2000, max=2020)])
    isbn = StringField('ISBN:',validators=[InputRequired(), Length(min=13, max=13)])
    conditionchoices = ['Fine/Like New', 'Good', 'Fair', 'Poor']
    book_condition = SelectField('Book Condition:', choices=conditionchoices, validators=[InputRequired()])
    price = IntegerField('Price:', validators=[InputRequired()])
    image = FileField('Book Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Submit')
    
class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    addressline1 = StringField('Address Line 1', validators=[InputRequired(), Length(min=2)])
    addressline2 = StringField('Address Line 2', validators=[InputRequired(), Length(min=2)])
    mobileno = StringField("Mobile No.", validators=[InputRequired(), Length(10)]) 
    profession = StringField('Profession', validators=[InputRequired(), Length(min=2)])
    dateofbirth = DateField("Date of Birth", validators=[InputRequired()])
    gender = RadioField('Gender', choices=[('male','Male'),('female','Female'),('other','Other')])
    submit = SubmitField('Submit')