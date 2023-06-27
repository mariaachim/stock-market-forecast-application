# Script to initialise the Flask instance
# Written by Maria Achim
# Started on 22nd June 2023

from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, Credentials # local import from models.py

from dotenv import load_dotenv # to handle environment variables

# standard libraries
import os

# loading environmental variables so i don't push credentials to github
load_dotenv()
username = os.getenv("DBUSER")
password = os.getenv("DBPASSWORD")
key = os.getenv("KEY")

app = Flask(__name__) # initialise flask application
app.config["SQLALCHEMY_DATABASE_URI"] = f"mariadb+mariadbconnector://{username}:{password}@127.0.0.1/cs-nea" # database connection
app.config['SECRET_KEY'] = key
db.init_app(app) # initialise database

with app.app_context():
    db.create_all() # creates database if it doesn't exist already
    db.session.commit()

# show login page automatically
@app.route('/')
def index():
    return redirect(url_for('login'))

def auth_index():
    return render_template('index.html')

@app.route('/login') # called when user navigates to login page
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST']) # called when POST request is sent by interaction
def login_post():
    username = request.form.get('username')
    password = request.form.get('psw')
    is_user = Credentials.query.filter_by(username=username, password=password).first()
    print(is_user) # debugging
    if not is_user:
        flash('Please check login details') # reloads page and shows authentication failed
        return render_template('login.html')
    return render_template('index.html') # if user is authenticated, redirect to index page

@app.route('/register') # called when user navigates to register page
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST']) # called when POST request is sent by interaction
def register_post():
    username = request.form.get('username')
    password = request.form.get('psw')
    password_confirmation = request.form.get('psw-confirmation')
    username_taken = Credentials.query.filter_by(username=username).first()
    invalid_account = False # boolean variable so that multiple messages can be shown
    if username_taken: # checking if username is already in database
        flash('Username is already taken')
        invalid_account = True
    elif password != password_confirmation: # checking if passwords are the same
        flash('Passwords do not match')
        invalid_account = True
    if invalid_account == True:
        return render_template('register.html')
    else:
        print("Valid credentials")
        new_user = Credentials(username=username, password=password) # creating new Credentials object
        db.session.add(new_user) # adding credentials to database
        db.session.commit()
        return render_template('login.html') # if account has been created

# to run with python -m app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)