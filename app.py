# Script to initialise the Flask instance
# Written by Maria Achim
# Started on 22nd June 2023

from flask import Flask, render_template, redirect, url_for, request, flash, get_flashed_messages, session
from flask_session import Session

from newsapi import NewsApiClient

#from forms import StocksSearchForm # NEW!!!!
from models import db, Credentials, Companies, Favourites # local import from models.py
import graphs
from quicksort import main_sort

from numpy import genfromtxt # for reading CSV file
from dotenv import load_dotenv # to handle environment variables

# standard libraries
import os
import random

# loading environmental variables so i don't push credentials to github
load_dotenv()
dbusername = os.getenv("DBUSER")
dbpassword = os.getenv("DBPASSWORD")
key = os.getenv("KEY")
api_key = os.getenv("API-KEY")

api = NewsApiClient(api_key = api_key)

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
        # get name of option from dict(record)['mic']
        graph_json = graphs.show_graph(dict(record)['mic'])
        return render_template('details.html', details=dict(record), userID=session['userID'], graph=graph_json) # converts record to dictionary so key-value pairs can be used in the template
    else: # run when /stocks page is rendered first
        company_objects = Companies.query.all() # list of Company objects
        names = [] # empty names list
        for i in range(len(company_objects)): # iterate through Company objects
            names.append(company_objects[i].name) # append company name to names list
        sorted = main_sort(names) # sort names
        return render_template('stocks.html', query=sorted) # records in companies database is processed by stocks.html

@app.route('/trendlines', methods=['POST']) # function triggered by POST request
def trendlines():
    option = list(request.form.keys())[0] # get POST request parameters
    graph_json = graphs.trendlines(option) # generate JSON object
    return render_template('trendlines.html', graph=graph_json) # pass JSON object into HTML template

@app.route('/forecasts', methods=['POST'])
def forecasts():
    mic = list(request.form.keys())[0] # get POST request parameters
    forecast = graphs.forecast_lstm(mic, "1y")
    graph_json = forecast[0] # default to showing past year with one month of predictions
    csv = graphs.get_csv(forecast[1]) # generate CSV file
    print(csv)
    return render_template('forecasts.html', name=mic, graph=graph_json, csv=csv) # renders template with MIC, graph JSON and CSV file

@app.route('/stock_favourites', methods=['POST'])
def stock_favourites():
    data = request.get_json() # get JSON-parsed data from POST request
    print(data) # for debugging purposes
    is_favourite = Favourites.query.filter_by(user_id=data['user_id'], company_id=data['company_id']).first()
    if not is_favourite: # check if already in favourites
        new_favourite = Favourites(user_id=data['user_id'], company_id=data['company_id'])
        db.session.add(new_favourite) # add entry to database
        db.session.commit() # data persists
        print("favourite added")
        return {'msg': 'Added to Favourites'}
    else:
        print("already in favourites")
        return {'msg': 'Already in Favourites'}
    
@app.route('/news')
def news():
    top_headlines = api.get_top_headlines(category='business') # gets articles with "business" tag
    #print(len(top_headlines['articles'])) # prints number of articles fetched from API
    if len(top_headlines['articles']) < 6:
        print("random.choices() used") # debugging, remove in prod
        articles = top_headlines['articles'] + random.choices(top_headlines['articles'], k=(6 - len(top_headlines['articles']))) # displays all articles and randomly selects with replacement
    else:
        print("random.sample() used") # debugging, remove in prod
        articles = random.sample(top_headlines['articles'], 6) # randomly selects 6 articles without replacement
    for i in range(len(articles)): # for improved terminal output readability
        print(articles[i])
    return render_template('news.html', articles=articles) # rendering template

@app.route('/favourites')
def favourites():
    # SQL query to find Companies with corresponding entry in Favourites using join statement
    results = db.session.query(Companies, Favourites).join(Favourites).filter(Favourites.user_id == session['userID']).all()
    favourites_names = []
    for company in results:
        favourites_names.append(company[0].name) # adding company names from query results
    sorted = main_sort(favourites_names) # sort names
    return render_template('favourites.html', query=sorted) # rendering template with company names list

@app.route('/heatmap', methods=['POST'])
def heatmap():
    # SQL query to find Companies with corresponding entry in Favourites using join statement
    results = db.session.query(Companies, Favourites).join(Favourites).filter(Favourites.user_id == session['userID']).all()
    favourites_mic = []
    for company in results:
        favourites_mic.append(company[0].mic) # adding company MICs from query results
    graph_json = graphs.heatmap(favourites_mic)
    return render_template('heatmap.html', graph=graph_json) # rendering template with company MICs list

# to run with python -m app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)