from models import Companies
from wtforms import Form, StringField, SelectField
from flask_sqlalchemy import SQLAlchemy

def test():
    industries = set()
    
    for value in Companies.query.distinct(Companies.industry):
        industries.add(value.industry)
    print(industries)

#class StocksSearchForm(Form):
    