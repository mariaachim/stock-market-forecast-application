# Script to initialise the Flask instance
# Written by Maria Achim
# Started on 22nd June 2023

from flask import Flask, render_template
from models import db

from dotenv import load_dotenv

import sys # standard library
import os

load_dotenv()
username = os.getenv("DBUSER")
password = os.getenv("DBPASSWORD")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"mariadb+mariadbconnector://{username}:{password}@127.0.0.1/cs-nea"
db.init_app(app)

with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)