# Script to initialise the Flask instance
# Written by Maria Achim
# Started on 22nd June 2023

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_session import Session

import yfinance as yf

#from forms import StocksSearchForm # NEW!!!!
from models import db, Credentials, Companies, Favourites # local import from models.py

from numpy import genfromtxt # for reading CSV file
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
    SESSION_TYPE='filesystem', # session files are stored inside flask_session local directory
    SECRET_KEY=key
)

Session(app) # initialise session
db.init_app(app) # initialise database

with app.app_context():
    # create list of tuples from reading CSV file contents
    data = genfromtxt('companies.csv', delimiter=',', skip_header=1, converters={0: lambda n: int(n), 1: lambda s: str(s.decode()), 2: lambda s: str(s.decode()), 3: lambda s: str(s.decode()), 4: lambda s: str(s.decode()), 5: lambda n: int(n), 6: lambda n: int(n)}).tolist()
    db.create_all() # creates database if it doesn't exist already
    for i in range(len(data)): # iterate over tuples in lists and creates Companies object
        company = Companies()
        company.company_id = data[i][0]
        company.name = data[i][1]
        company.mic = data[i][2]
        company.industry = data[i][3]
        company.ceo = data[i][4]
        company.year_founded = data[i][5]
        company.num_employees = data[i][6]
        is_in_db = Companies.query.filter_by(company_id=company.company_id).first() # check if line already in table
        if not is_in_db:
            db.session.add(company) # adds data to Companies table
    db.session.commit() # makes changes persist

favourites = []

@app.route('/')
def index():
    if 'user' in session: # if session is created
        return render_template('index.html')
    else: # to redirect user to login page so session can be created
        return redirect(url_for('login')) # GET request

@app.route('/login') # called when user navigates to login page
def login():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('psw')
        is_user = Credentials.query.filter_by(username=username, password=password).first()
        print(is_user)
        if not is_user:
            flash('Please check login details', 'error') # reloads page and shows authentication failed
            return render_template('login.html')
        else:
            session['user'] = request.form.get('username') # only store username in session data
            session['userID'] = is_user.user_id # store user_id so new record to Favourites table can be created
            return redirect(url_for('index')) # if user is authenticated, redirect to index page
    else:
        return render_template('login.html')

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
        flash('Username is already taken and passwords do not match', 'error')
    elif username_taken: # checking if username is already in database
        flash('Username is already taken', 'error')
    elif password != password_confirmation: # checking if passwords are not the same
        flash('Passwords do not match', 'error')
    else:
        print("Valid credentials")
        new_user = Credentials(username=username, password=password) # creating new Credentials object
        db.session.add(new_user) # adding credentials to database
        db.session.commit()
        flash('Account created', 'error')
        return render_template('login.html') # if account has been created
    return render_template('register.html')    

@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    if request.method == 'POST': # run when button is pressed
        details = Companies.query.filter_by(name=list(request.form.keys())[0]).first() # gets record based on name of company
        record = []
        for i in list(vars(details).items()): # list of tuples
            if i[0] != "_sa_instance_state": # removes unnecessary attribute
                record.append(i) # adds tuple to record list
        print(dict(record))
        #data = yf.Ticker(dict(record)['mic'])
        return render_template('details.html', details=dict(record), userID=session['userID']) # converts record to dictionary so key-value pairs can be used in the template
    else: # run when /stocks page is rendered first
        return render_template('stocks.html', query=Companies.query.all()) # records in companies database is processed by stocks.html

@app.route('/stockfavourites', methods=['POST'])
def stockfavourites():
    data = request.get_json() # get JSON-parsed data from POST request
    print(data) # for debugging purposes
    is_favourite = Favourites.query.filter_by(user_id=data['userID'], company_id=data['companyID']).first()
    if not is_favourite: # check if already in favourites
        new_favourite = Favourites(user_id=data['userID'], company_id=data['companyID'])
        db.session.add(new_favourite) # add entry to database
        db.session.commit() # data persists
        print("favourite added")
        flash('Added to Favourites', 'error')
        return {'code': 'success'} # server responds with success
    else:
        print("already in favourites")
        return {'code': 'error'} # server responds with error
    
@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/favourites')
def favourites():
    return render_template('favourites.html')

# to run with python -m app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)