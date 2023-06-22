import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'Credentials'
    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(length=50), nullable=False)
    password = sqlalchemy.Column(sqlalchemy.String(length=50), nullable=False)