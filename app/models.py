from app import app
from flask_sqlalchemy import SQLAlchemy

# initialize the db
db = SQLAlchemy(app)


# Models
# User Model
class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    created_at = db.Column(db.String())


# User Profile Model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_photo = db.Column(db.String(80))
    username = db.Column(db.String(50), unique=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    dob = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    phonenumber = db.Column(db.Integer, unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('profile', cascade="all, delete-orphan"), lazy='joined')
