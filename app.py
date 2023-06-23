# Script to initialise the Flask instance
# Written by Maria Achim
# Started on 22nd June 2023

from flask import Flask, render_template
from models import db # local import

from dotenv import load_dotenv

# standard libraries
import os

# loading environmental variables so i don't push credentials to github
load_dotenv()
username = os.getenv("DBUSER")
password = os.getenv("DBPASSWORD")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"mariadb+mariadbconnector://{username}:{password}@127.0.0.1/cs-nea" # database connection
db.init_app(app)

with app.app_context():
    db.create_all() # creates database if it doesn't exist already
    db.session.commit()

# show login page automatically
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

# to run with python -m app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)