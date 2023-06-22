import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Favourites(Base):
    __tablename__ = 'Favourites'
    