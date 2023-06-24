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

app = Flask(__name__) # initialise flask application
app.config["SQLALCHEMY_DATABASE_URI"] = f"mariadb+mariadbconnector://{username}:{password}@127.0.0.1/cs-nea" # database connection
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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    is_user = Credentials.query.filter_by(username=username).first()
    print(is_user)
    if not is_user:
        flash('Please check login details')
    return render_template('index.html')

# to run with python -m app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)