from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField

class RegisterForm(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')
    submit = SubmitField('submit')