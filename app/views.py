# import required modules
import os
from flask import jsonify, request, abort
import uuid
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import db,Profile,User
from app import app
import jwt
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({"message":"Token is missing"}), 401
        
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            current_user = User.query.filter_by(id=data.get('id')).first()
        except:
            return jsonify({"message":"Token is invalid"}), 401
        
        return f(current_user, *args, **kwargs)
        
    return decorated

# Create a new user
@app.route('/api/v1/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data.get('password'), method='sha256')
    new_user = User(id=str(uuid.uuid4()), email=data.get('email'), password=hashed_password, admin=False,
                    created_at=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


# Login user
@app.route('/api/v1/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({"message": "Invalid email or password!"}), 401

    user = User.query.filter_by(email=auth.username).first()
    if not user:
        return jsonify({"message": "Invalid email or password!"}), 401
    
    if check_password_hash(user.password,auth.password):
        token = jwt.encode({'id': user.id},app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')}), 200

    return jsonify({"message": "Invalid email or password!"}), 401

# get all users in db
@app.route('/api/v1/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({"message": "Cannot perform that action"}), 401
    users = User.query.all()
    if not users:
        abort(204, message="No users found") 
    output = []
    for user in users:
        user_data = {'user_id': user.id, 'email': user.email, 'password': user.password, 'admin': user.admin,
                     'created_at': user.created_at}
        output.append(user_data)

    return jsonify({"users": output}), 200


# get one user from db with id supplied
@app.route('/api/v1/user/<user_id>', methods=['GET'])
@token_required
def get_one_user(current_user,user_id):
    if not current_user.admin:
        return jsonify({"message": "Cannot perform that action"}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        abort(404, message="User not found")

    user_data = {'user_id': user.user_id, 'email': user.email, 'password': user.password, 'admin': user.admin,
                 'created_at': user.created_at}
    return jsonify({"user": user_data}), 200


# delete user with id supplied from db
@app.route('/api/v1/user/<user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user,user_id):
    if not current_user.id == user_id:
        return jsonify({"message": "Cannot perform that action"}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return abort(404 ,message="User not found")

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "user deleted"}), 200


# Create users profile
@app.route('/api/v1/profile', methods=['POST'])
@token_required
def create_user_profile(current_user):
    data = request.get_json()
    if not current_user.id == data.get('user_id'):
        return jsonify({"message": "Cannot perform that action"}), 401

    user = User.query.filter_by(id=data.get('user_id')).first()
    if not user:
        return abort(404, message="User not found")
    
    # save profile photo
    filepath = os.path.join(app.config['UPLOAD_PATH'], 'no_profile_photo.png')
    if 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400, message="Invalid file")

            filename = data.get('user_id') + file_ext
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            filepath = os.path.join(app.config['UPLOAD_PATH'], filename)

    user_profile = Profile(username=data.get('username'),
                           profile_photo=filepath,
                           firstname=data.get('firstname'),
                           lastname=data.get('lastname'),
                           dob=data.get('dob'),
                           gender=data.get('gender'),
                           phonenumber=data.get('phonenumber'),
                           user_id=data.get('user_id')
                           )

    db.session.add(user_profile)
    db.session.commit()
    return jsonify({"message": "User Profile created"}), 201


# get all profiles in db
@app.route('/api/v1/profile', methods=['GET'])
@token_required
def get_all_profiles(current_user):
    if not current_user.admin:
        return jsonify({"message": "Cannot perform that action"}), 401
    profiles = Profile.query.all()
    if not profiles:
        return abort(404, message="No profiles found")
    output = []
    for profile in profiles:
        profile_data = {'user_id': profile.user_id, 'phonenumber': profile.phonenumber, 'gender': profile.gender,
                        'dob': profile.dob, 'firstname': profile.firstname, 'lastname': profile.lastname,
                        'username': profile.username, 'profile_photo': profile.profile_photo}
        output.append(profile_data)

    return jsonify({"profiles": output}), 200


# get one profile from db
@app.route('/api/v1/profile/<user_id>', methods=['GET'])
@token_required
def get_user_profile(current_user,user_id):
    if not current_user.id == user_id:
        return jsonify({"message": "Cannot perform that action"}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        abort(404, message="User not found")

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        abort(404, message="Profile not found")

    profile_data = {'id': profile.id, 'user_id': profile.user_id, 'phonenumber': profile.phonenumber,
                    'gender': profile.gender, 'dob': profile.dob, 'firstname': profile.firstname,
                    'lastname': profile.lastname, 'username': profile.username, 'profile_photo': profile.profile_photo}

    return jsonify({"profile": profile_data}), 200


# update profile in db
@app.route('/api/v1/profile/<user_id>', methods=['PUT'])
@token_required
def update_profile(current_user,user_id):
    data = request.get_json()
    if not current_user.id == user_id:
        return jsonify({"message": "Cannot perform that action"}), 401

    user = User.query.filter_by(id=user_id).first()
    if not user:
        abort(404, message="User not found")

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        abort(404, message="Profile not found")

    # check if profile photo is changed
    if 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400, message="Invalid file")
            filename = data.get('user_id') + file_ext
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            filepath = os.path.join(app.config['UPLOAD_PATH'], filename)
            profile.profile_photo = filepath

    profile.username = data.get('username')
    profile.firstname = data.get('firstname')
    profile.lastname = data.get('lastname')
    profile.dob = data.get('dob')
    profile.gender = data.get('gender')
    profile.phonenumber = data.get('phonenumber')
    db.session.commit()

    return jsonify({"message": "Profile has been updated"}), 200
