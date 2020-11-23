from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField,RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo,NumberRange

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # confirm_password = PasswordField('n_confirm_password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SellBooksForm(FlaskForm):
    book_name = StringField('Book Name:', validators=[DataRequired(), Length(min=2, max=20)])
    author_name = StringField('Author Name:', validators=[DataRequired(), Length(min=2, max=20)])
    publication_name = StringField('Publication Name:', validators=[DataRequired(), Length(min=2, max=20)])
    edition = IntegerField('Edition:', validators=[DataRequired(),NumberRange(min=2000, max=2020)])
    price = IntegerField('Price:', validators=[DataRequired()])
    
class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    addressline1 = StringField('Address Line 1',validators=[DataRequired(), Length(min=2)])
    addressline2 = StringField('Address Line 2',validators=[DataRequired(), Length(min=2)])
    mobileno = StringField("Mobile No.", validators=[DataRequired(), Length(10)]) 
    profession = StringField('Profession',validators=[DataRequired(), Length(min=2)])
    # dateofbirth = DateField("Date of Birth", validators=[DateRange(date(1950,1,1), date(2020,12,30))])
    dateofbirth = DateField("Date of Birth", validators=[DataRequired()])
    gender = RadioField('Gender', choices=[('male','Male'),('female','Female'),('other','Other')])
    submit = SubmitField('Submit')