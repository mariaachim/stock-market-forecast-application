from numpy import genfromtxt
from flask_sqlalchemy import SQLAlchemy # just sqlalchemy because no flask
from dotenv import load_dotenv
import os

def load_data(filename):
    data = genfromtxt(filename, delimiter=',', skip_header=1, converters={0: lambda s: str(s.decode()), 1: lambda s: str(s.decode()), 2: lambda s: str(s.decode()), 3: lambda n: int(n), 4: lambda n: int(n)})
    return data.tolist()

data = load_data('companies.csv')

load_dotenv()
dbusername = os.getenv("DBUSER")
dbpassword = os.getenv("DBPASSWORD")

engine = SQLAlchemy.create_engine(f"mariadb+mariadbconnector://{dbusername}:{dbpassword}@127.0.0.1/cs-nea")

print(data)