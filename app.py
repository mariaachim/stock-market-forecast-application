# Script to initialise the Flask instance
# Written by Maria Achim
# Started on 22nd June 2023

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_session import Session
from models import db, Credentials # local import from models.py

from dotenv import load_dotenv # to handle environment variables

# standard libraries
import os

# loading environmental variables so i don't push credentials to github
load_dotenv()
dbusername = os.getenv("DBUSER")
dbpassword = os.getenv("DBPASSWORD")
key = os.getenv("KEY")

app = Flask(__name__) # initialise flask application
app.config["SQLALCHEMY_DATABASE_URI"] = f"mariadb+mariadbconnector://{dbusername}:{dbpassword}@127.0.0.1/cs-nea" # database connection
app.config.update(
    SESSION_TYPE='filesystem',
    SECRET_KEY=key
)
Session(app)
db.init_app(app) # initialise database

with app.app_context():
    db.create_all() # creates database if it doesn't exist already
    db.session.commit()

# show login page automatically
@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

def auth_index():
    return render_template('index.html')

@app.route('/login') # called when user navigates to login page
def login():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST']) # called when POST request is sent by interaction
def login_post():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('psw')
        is_user = Credentials.query.filter_by(username=username, password=password).first()
        if not is_user:
            flash('Please check login details') # reloads page and shows authentication failed
            return render_template('login.html')
        else:
            session['user'] = request.form.get('username')
            session['passwd'] = request.form.get('psw')
            return redirect(url_for('index')) # if user is authenticated, redirect to index page
    else:
        return render_template('login.html')
# TODO redirects to /login when authenticated but with index.html

@app.route('/register') # called when user navigates to register page
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST']) # called when POST request is sent by interaction
def register_post():
    username = request.form.get('username')
    password = request.form.get('psw')
    password_confirmation = request.form.get('psw-confirmation')
    username_taken = Credentials.query.filter_by(username=username).first()
    if username_taken and password != password_confirmation: # checking if username is already in database and passwords are not the same
        flash('Username is already taken and passwords do not match')
    elif username_taken: # checking if username is already in database
        flash('Username is already taken')
    elif password != password_confirmation: # checking if passwords are not the same
        flash('Passwords do not match')
    else:
        print("Valid credentials")
        new_user = Credentials(username=username, password=password) # creating new Credentials object
        db.session.add(new_user) # adding credentials to database
        db.session.commit()
        flash('Account created')
        return render_template('login.html') # if account has been created
    return render_template('register.html')    

# to run with python -m app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)