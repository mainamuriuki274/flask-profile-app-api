from app import app
from flask_sqlalchemy import SQLAlchemy

# initialize the db
db = SQLAlchemy(app)


# Models
# User Model
class User(db.Model):
    id = db.Column(db.String(50), nullable=False, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean)
    created_at = db.Column(db.String())


# User Profile Model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_photo = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phonenumber = db.Column(db.Integer, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    user = db.relationship('User', backref=db.backref('profile', cascade="all, delete-orphan"), lazy='joined')
