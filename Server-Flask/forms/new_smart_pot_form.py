from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField

class NewSmartPotForm(FlaskForm):
    name = StringField('name')
    serial_number = StringField('serial_number')
    location = StringField('location')
    plant_name = StringField('plant_name')
    desired_humidity = StringField('desired_humidity')
    watering_frequency = SelectField('watering_frequency')
    submit = SubmitField('submit')