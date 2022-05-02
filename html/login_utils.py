import hashlib

from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

"""
User creation
"""


class User(UserMixin):
    def __init__(self, id_param, username, password):
        self.name = username
        self.id = id_param
        self.password = password

    def set_password(self, password):
        self.password = hashlib.sha3_512(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return hashlib.sha3_512(password.encode('utf-8')).hexdigest().strip() == self.password.strip()

    def __repr__(self):
        return '<User {}>'.format(self.name)


class LoginForm(FlaskForm):
    email = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')
