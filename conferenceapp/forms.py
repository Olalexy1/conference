from re import M
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField

from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField("Your Email", validators=[DataRequired(),Email()])

    pwd = PasswordField("Enter your password")

    loginbtn = SubmitField("Login")


class ContactusForm(FlaskForm):
    fullname = StringField("Your FullName", validators=[DataRequired()])

    email = StringField("Your email:", validators=[DataRequired(), Email()])

    message = TextAreaField("Your Message", validators=[DataRequired()])

    btn = SubmitField("Submit")

