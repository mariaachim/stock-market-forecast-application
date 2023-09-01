from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Credentials(db.Model):
    __tablename__ = 'Credentials'
    user_id = db.Column(db.Integer, primary_key=True) # user_id is primary key
    username = db.Column(db.String(length=50), nullable=False, unique=True)
    password = db.Column(db.String(length=50), nullable=False)

    def __repr__(self): # function for debugging purposes
        return f'<User {self.username}>'

class Companies(db.Model):
    __tablename__ = 'Companies'
    company_id = db.Column(db.Integer, primary_key=True) # company_id is primary key
    name = db.Column(db.String(length=50), nullable=False)
    mic = db.Column(db.String(length=4), nullable=False)
    industry = db.Column(db.String(length=50), nullable=False)
    ceo = db.Column(db.String(length=50), nullable=False)
    year_founded = db.Column(db.Integer, nullable=False)
    num_employees = db.Column(db.Integer, nullable=False)

    def __repr__(self): # function for debugging purposes
        return self.name
    
class Favourites(db.Model):
    __tablename__ = 'Favourites'
    # composite primary key
    user_id = db.Column(db.Integer, db.ForeignKey('Credentials.user_id'), primary_key=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('Companies.company_id'), primary_key=True, nullable=False)

    def __repr__(self): # function for debugging purposes
        return f'<Favourites: User {self.user_id}, Company {self.company_id}>'