from flask import Flask, render_template, url_for, flash, redirect # allow rendering of html code rather than printing it raw
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

import secrets
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_bcrypt import Bcrypt


app=Flask(__name__)
#flask_bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'e8bfce50659d76e727e7a2e5ca165a8a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(50), nullable=False)
  
  def __repr__(self):
    return f"User('{self.username}', '{self.email}')"

@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        pw_hash =generate_password_hash(form.password.data, method='sha256')
        #pw_hash = flask_bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password = pw_hash )
        try:
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError:
            flase('user exist')
        else:
            flash(f'Account created for {form.username.data}!', 'success')
        finally:
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)
  
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                flash('Logged in successfully!', category='success')
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('User name does not exist', category='error')
        return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)
    
@app.route("/about")
def about():
    return render_template("about.html")
    
if (__name__ == "__main__"):
    app.run(debug=True, host="0.0.0.0")
