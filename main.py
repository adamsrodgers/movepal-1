from flask import Flask, render_template, url_for, flash, redirect # allow rendering of html code rather than printing it raw
#from flask_wtf import FlaskForm
#from wtforms import StringField, PasswordField, SubmitField, BooleanField
#from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_login import login_user, login_required
import secrets
from forms import RegistrationForm, LoginForm, SearchForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from api import for_sale_list, get_attom_data, parse_for_sale_list#######################testing
import pandas as pd
#from SQLAlchemy import create_engine
from api_output import for_sale_list_data


app=Flask(__name__)
flask_bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'e8bfce50659d76e727e7a2e5ca165a8a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
login_status=False #THIS GETS TURNED TO TRUE ONCE THE USER LOGS IN
house_list={} #THIS IS WHERE THE PARSED HOUSE SEARCH GETS STORED

#house_list=parse_for_sale_list(for_sale_list_data)#TESTING
#house_list[0]=get_attom_data(house_list[0])#TESTING

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False) 
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

db.create_all()




'''
class SavedHouses(db.Model):
    pass
'''

@app.route("/")
def home_page():
    return render_template("home.html", login_status=login_status)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=bcrypt.generate_password_hash(
                form.password.data).decode('utf-8'))
        
#         pw_hash =generate_password_hash(form.password.data, method='sha256')
        #pw_hash = flask_bcrypt.generate_password_hash(form.password.data)
#         user = User(username=form.username.data, email=form.email.data, password = pw_hash )
        try:
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError:
            flash('user exist')
        else:
            flash(f'Account created for {form.username.data}!', 'success')
        finally:
            return redirect(url_for('home_page'))
    return render_template('register.html', title='Register', form=form, login_status=login_status)
  
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                flash('Logged in successfully!', category='success')
#                login_user(my_user, remember=form.remember.data)

                global login_status
                login_status=True
                return redirect(url_for('home_page'))
                #return render_template('home_logged.html')
            else:
                flash('Incorrect password, try again.', category='error')
                return redirect(url_for('login'))
        else:
            flash('User name does not exist', category='error')
            return redirect(url_for('home_page'))
    return render_template('login.html', title='Login', form=form, login_status=login_status)

@app.route("/logout")
def logout():
    global login_status
    login_status = False
    flash('logged out successfully!', category = 'success')
    return redirect(url_for('home_page'))

@app.route("/about")
def about():
    return render_template("about.html", login_status=login_status)

@app.route("/search", methods=['GET', 'POST'])
def search():
    form=SearchForm()
    #print(form.state.data)
    #print(form.maximum_hoa.data)
    if(form.state.data != None):
        querystring={}
        querystring["offset"]="0"
        querystring["limit"]="42"
        querystring["state_code"]=str(form.state.data)
        querystring["city"]=str(form.city.data)
        if(form.sort_by.data != None):
            querystring["sort"]=str(form.sort_by.data)
        if(form.minimum_price.data != None):
            querystring["price_min"]=str(form.minimum_price.data)
        if(form.maximum_price.data != None):
            querystring["price_max"]=str(form.maximum_price.data)
        if(form.minimum_beds.data != None):
            querystring["beds_min"]=str(form.minimum_beds.data)
        if(form.maximum_beds.data != None):
            querystring["beds_max"]=str(form.maximum_beds.data)
        if(form.minimum_baths.data != None):
            querystring["baths_min"]=str(form.minimum_baths.data)
        if(form.maximum_baths.data != None):
            querystring["baths_max"]=str(form.maximum_baths.data)
        if(form.maximum_hoa.data != None):
            querystring["hoa_max"]=str(form.maximum_hoa.data)
        #print(querystring)
        global house_list
        house_list=for_sale_list(querystring)
        #print(house_list)
        #house_list=parse_for_sale_list(for_sale_list_data)
        #print(house_list)
        #return redirect(url_for('display_search', data=house_list))
        return redirect(url_for('display_search'))#, data=house_list
    return render_template('search_houses.html', form=form, login_status=login_status)

@app.route("/search/display")
def display_search():
    return render_template('display_search.html', login_status=login_status, data=house_list)

@app.route("/search/display/<movepal_id>")
def more_information(movepal_id):
    house_list[int(movepal_id)]=get_attom_data(house_list[int(movepal_id)])
    return render_template('more_information.html', login_status=login_status, data=house_list[int(movepal_id)])
'''get_attom_data(house_list[int(movepal_id)])'''

@app.route("/saved")
def saved():
    #to be changed
    return redirect(url_for('home_page'))
'''
@app.route("/home_logged")
def home_logged():
    return render_template("home_logged.html")
'''


    
if (__name__ == "__main__"):
    app.run(debug=True, host="0.0.0.0")
#0.0.0.0")
#a