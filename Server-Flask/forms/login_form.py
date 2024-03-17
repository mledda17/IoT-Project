from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField

class LoginForm(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')
    remember_me = BooleanField('remember_me')
    submit = SubmitField('submit')