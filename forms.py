# for searching and filtering

from models import Companies
from wtforms import Form, StringField, SelectField
from flask_sqlalchemy import SQLAlchemy

class StocksSearchForm(Form):
    industries = set()
    for value in Companies.query.distinct(Companies.industry):
        industries.add(value.industry)

    choices = [(x, x) for x in industries]
    select = SelectField("Search by industry:", choices=choices)
    search = StringField("")
