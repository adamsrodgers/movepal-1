from flask_wtf import FlaskForm
import secrets
from wtforms import StringField, SelectField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask import Flask, render_template, url_for, flash, redirect

#create some fields

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    state_list=[('AL','Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')]
    city = StringField('City (Required)', validators=[DataRequired()])
    state = SelectField('State (Required)', choices=state_list, validators=[DataRequired()])
    sort_by = SelectField('Sort by', choices=[('relevant', 'Relevance'), ('newest', 'Newest'), ('lowest_price', 'Lowest_price'), ('highest_price', 'Highest_price'), ('largest_sqft', 'Largest sqft size'), ('lot_size', 'Lot size')])
    minimum_price = IntegerField('Minimum price')
    maximum_price = IntegerField('Maximum price')
    minimum_beds = IntegerField('Minimum bedrooms')
    maximum_beds = IntegerField('Maximum bedrooms')
    minimum_baths = IntegerField('Minimum bathrooms')
    maximum_baths = IntegerField('Maximum bathrooms')
    maximum_hoa = IntegerField('Maximum HOA fee')
    submit = SubmitField('Search')