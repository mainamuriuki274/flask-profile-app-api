from enum import unique
import os
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['UPLOAD_PATH'] = os.getenv("UPLOAD_PATH")
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
app.config.from_object("config")


db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    created_at = db.Column(db.String())

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_photo = db.Column(db.String(80))
    username = db.Column(db.String(50), unique=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    dob = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    phonenumber = db.Column(db.Integer, unique=True ,nullable=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('profile', cascade="all, delete-orphan"),lazy='joined')


# Create a new user
@app.route('/user/register', methods = ['POST'])
def create_user():
    data = request.form
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(id=str(uuid.uuid4()), email=data['email'], password=hashed_password, admin=False, created_at=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"})

# Login user
@app.route('/user/login', methods = ['POST'])
def login_user():
    data = request.form
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"message": "User not found"})
    if check_password_hash(user.password, data['password']):
        user_data = {}
        user_data['user_id'] = user.user_id 
        user_data['email'] = user.email 
        user_data['password'] = user.password 
        user_data['admin'] = user.admin 
        user_data['created_at'] = user.created_at 
        return jsonify({"user": user_data})
    return jsonify({"message": "Invalid email or password!"})

# get all users in db
@app.route('/user', methods = ['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['user_id'] = user.id 
        user_data['email'] = user.email 
        user_data['password'] = user.password 
        user_data['admin'] = user.admin 
        user_data['created_at'] = user.created_at 
        output.append(user_data)

    return jsonify({"users": output})

# get one user from db with id supplied
@app.route('/user/<user_id>', methods = ['GET'])
def get_one_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user_data = {}
    user_data['user_id'] = user.user_id 
    user_data['email'] = user.email 
    user_data['password'] = user.password 
    user_data['admin'] = user.admin 
    user_data['created_at'] = user.created_at 
    

    return jsonify({"user": user_data})

# delete user with id supplied from db
@app.route('/user/<user_id>', methods = ['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"})

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "user deleted"})


# Create users profile
@app.route('/profile', methods = ['POST'])
def create_user_profile():
    data = request.form
    user = User.query.filter_by(id=data['user_id']).first()
    if not user:
        return jsonify({"message": "User not found"})

    filepath = os.path.join(app.config['UPLOAD_PATH'], 'no_profile_photo.png')
    if 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            filename = data['user_id'] + file_ext
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            filepath = os.path.join(app.config['UPLOAD_PATH'], filename)
            profile.profile_photo = filepath
    
    user_profile = Profile( username=data['username'], 
                            profile_photo = filepath,
                            firstname=data['firstname'],
                            lastname=data['lastname'], 
                            dob=data['dob'],
                            gender=data['gender'],
                            phonenumber=data['phonenumber'],
                            user_id = data['user_id']
                            )
    
    db.session.add(user_profile)
    db.session.commit()
    return jsonify({"message": "User Profile created"})

# get all profiles in db
@app.route('/profile', methods = ['GET'])
def get_all_profiles():
    profiles = Profile.query.all()
    output = []
    for profile in profiles:
        profile_data = {}
        profile_data['user_id'] = profile.user_id 
        profile_data['phonenumber'] = profile.phonenumber 
        profile_data['gender'] = profile.gender 
        profile_data['dob'] = profile.dob 
        profile_data['firstname'] = profile.firstname 
        profile_data['lastname'] = profile.lastname 
        profile_data['username'] = profile.username 
        profile_data['profile_photo'] = profile.profile_photo 
        output.append(profile_data)

    return jsonify({"profiles": output})

# get one profile from db
@app.route('/profile/<user_id>', methods = ['GET'])
def get_user_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        abort(404)
    profile_data = {}
    profile_data['id'] = profile.id
    profile_data['user_id'] = profile.user_id
    profile_data['phonenumber'] = profile.phonenumber 
    profile_data['gender'] = profile.gender 
    profile_data['dob'] = profile.dob 
    profile_data['firstname'] = profile.firstname 
    profile_data['lastname'] = profile.lastname 
    profile_data['username'] = profile.username 
    profile_data['profile_photo'] = profile.profile_photo 

    return jsonify({"profile": profile_data})

# update profile in db
@app.route('/profile/<profile_id>', methods = ['PUT'])
def update_profile(profile_id):
    data = request.form
    user = User.query.filter_by(id=data['user_id']).first()
    if not user:
        return jsonify({"message": "no user found"})
    
    profile = Profile.query.filter_by(id=profile_id).first()
    if not profile:
        abort(404)
    
    if 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            filename = data['user_id'] + file_ext
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            filepath = os.path.join(app.config['UPLOAD_PATH'], filename)
            profile.profile_photo = filepath
    
    profile.username = data['username']
    profile.firstname = data['firstname']
    profile.lastname = data['lastname']
    profile.dob = data['dob']
    profile.gender = data['gender']
    profile.phonenumber = data['phonenumber']
    db.session.commit()

    return jsonify({"message":"Profile has been updated"})
    
    


    db.session.commit()
    return jsonify({"message":"User has been promoted"})


if __name__ == "__main__":
    app.run()