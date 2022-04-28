from flask_login import UserMixin
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import validators, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class User(UserMixin):
    def __init__(self,id, username, password):
        self.name = username
        self.id = id
        self.password = generate_password_hash(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)

class LoginForm(FlaskForm):
    email = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')

