import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'Companies'
    company_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(length=50), nullable=False)
    industry = sqlalchemy.Column(sqlalchemy.String(length=50), nullable=False)
    ceo = sqlalchemy.Column(sqlalchemy.String(length=50), nullable=False)
    year_founded = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    num_employees = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)