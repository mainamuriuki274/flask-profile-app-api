# import required modules
import os
from flask import jsonify, request, abort
import uuid
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, Profile, User
from app import app
import jwt
from functools import wraps
import base64


def save_image(encoded_image, extension, current_user, ):
    image = base64.urlsafe_b64decode(encoded_image)
    ext = None
    if extension == 'data:image/png;base64':
        ext = '.png'
    elif extension == 'data:image/jpg;base64':
        ext = '.jpg'
    elif extension == 'data:image/jpeg;base64':
        ext = '.jpeg'

    filename = current_user + ext
    filepath = app.config['UPLOAD_PATH'] + filename
    with open(filepath, 'wb') as f:
        f.write(image)

    return app.config['UPLOAD_PATH'] + filename


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], 'UTF-8')
            current_user = User.query.filter_by(id=data.get('id')).first()
        except:
            return jsonify({"message": "Token is invalid"}), 401

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
    user = User.query.filter_by(email=data.get('email')).first()
    token = jwt.encode({'id': user.id}, app.config['SECRET_KEY'])
    return jsonify({"message": "User created", 'token': token.decode('UTF-8')}), 201


# Login user
@app.route('/api/v1/login', methods=['GET'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({"message": "Invalid email or password!"}), 401

    user = User.query.filter_by(email=auth.username).first()
    if not user:
        return jsonify({"message": "Invalid email or password!"}), 401

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'id': user.id}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')}), 200

    return jsonify({"message": "Invalid email or password!"}), 401


# update email in db
@app.route('/api/v1/user/email', methods=['PUT'])
@token_required
def update_email(current_user):
    data = request.get_json()
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        abort(404)

    user.email = data.get('email')
    db.session.commit()
    return jsonify({"message": "User email has been updated"}), 200


# update password in db
@app.route('/api/v1/user/password', methods=['PUT'])
@token_required
def update_password(current_user):
    data = request.get_json()
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        abort(404)
    if not check_password_hash(user.password, data.get('password')):
        abort(401)

    user.password = generate_password_hash(data.get('newPassword'), method='sha256')
    db.session.commit()

    return jsonify({"message": "User password has been updated"}), 200


# get all users in db
@app.route('/api/v1/users', methods=['GET'])
def get_users():
    users = User.query.all()
    if not users:
        abort(204)
    output = []
    for user in users:
        user_data = {'user_id': user.id, 'email': user.email, 'password': user.password, 'admin': user.admin,
                     'created_at': user.created_at}
        output.append(user_data)

    return jsonify({"users": output}), 200


# get one user from db with id supplied
@app.route('/api/v1/user', methods=['GET'])
@token_required
def get_user(current_user):
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        abort(404)

    user_data = {'email': user.email, 'password': user.password, 'admin': user.admin,
                 'created_at': user.created_at}
    return jsonify({"user": user_data}), 200


# check if email exists
@app.route('/api/v1/email/<email>', methods=['GET'])
def get_email(email):
    email = User.query.filter_by(email=email).first()
    if email:
        return jsonify({"message": "Email exists"}), 409
    else:
        return jsonify({"message": "Email does not exists"}), 200


# check if username exists
@app.route('/api/v1/username/<username>', methods=['GET'])
def get_username(username):
    username = Profile.query.filter_by(username=username).first()
    if username:
        return jsonify({"message": "Username exists"}), 409
    else:
        return jsonify({"message": "Username does not exists"}), 200


# check if phonenumber exists
@app.route('/api/v1/phonenumber/<phonenumber>', methods=['GET'])
def get_phonenumber(phonenumber):
    phonenumber = Profile.query.filter_by(phonenumber=phonenumber).first()
    if phonenumber:
        return jsonify({"message": "Phonenumber exists"}), 409
    else:
        return jsonify({"message": "Phonenumber does not exists"}), 200


# delete user with id supplied from db
@app.route('/api/v1/user', methods=['DELETE'])
@token_required
def delete_user(current_user):
    data = request.get_json()
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        return abort(404)

    if not check_password_hash(user.password, data.get('password')):
        abort(401)

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "user deleted"}), 200


# Create users profile
@app.route('/api/v1/profile', methods=['POST'])
@token_required
def create_user_profile(current_user):
    data = request.get_json()
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        return abort(404)

    # save profile photo
    if not data.get('img'):
        abort(400)

    encoded_image = data.get('img')
    extension = encoded_image.split(",")[0]
    if extension not in app.config['UPLOAD_EXTENSIONS']:
        abort(400)
    filepath = save_image(encoded_image.split(",")[1], extension, current_user.id)

    user_profile = Profile(username=data.get('username'),
                           profile_photo=filepath,
                           firstname=data.get('firstname'),
                           lastname=data.get('lastname'),
                           dob=data.get('dob'),
                           gender=data.get('gender'),
                           phonenumber=data.get('phonenumber'),
                           user_id=current_user.id
                           )

    db.session.add(user_profile)
    db.session.commit()
    return jsonify({"message": "User Profile created"}), 201


# get all profiles in db
@app.route('/api/v1/profiles', methods=['GET'])
@token_required
def get_all_profiles(current_user):
    if not current_user.admin:
        return jsonify({"message": "Cannot perform that action"}), 401
    profiles = Profile.query.all()
    if not profiles:
        return abort(404)
    output = []
    for profile in profiles:
        profile_data = {'user_id': profile.user_id, 'phonenumber': profile.phonenumber, 'gender': profile.gender,
                        'dob': profile.dob, 'firstname': profile.firstname, 'lastname': profile.lastname,
                        'username': profile.username, 'profile_photo': profile.profile_photo}
        output.append(profile_data)

    return jsonify({"profiles": output}), 200


# get one profile from db
@app.route('/api/v1/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        abort(404)

    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        abort(404)

    ext = profile.profile_photo.split(".")[-1]
    with open(os.path.abspath(os.getcwd()) + profile.profile_photo, "rb") as f:
        img = f.read()
    data = base64.b64encode(img).decode()
    src = "data:image/{ext};base64,{data}".format(ext=ext, data=data)

    profile_data = {'id': profile.id, 'user_id': profile.user_id, 'phonenumber': profile.phonenumber,
                    'gender': profile.gender, 'dob': profile.dob, 'firstname': profile.firstname,
                    'lastname': profile.lastname, 'username': profile.username, 'profile_photo': src,
                    'email': user.email}

    return jsonify({"profile": profile_data}), 200


# update profile in db
@app.route('/api/v1/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        abort(404)

    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        abort(404)

    # check if profile photo is changed
    if data.get('img'):
        # save profile photo
        encoded_image = data.get('img')
        extension = encoded_image.split(",")[0]
        if extension not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        filepath = save_image(encoded_image.split(",")[1], extension, current_user.id)
        profile.profile_photo = filepath

    profile.username = data.get('username')
    profile.firstname = data.get('firstname')
    profile.lastname = data.get('lastname')
    profile.dob = data.get('dob')
    profile.gender = data.get('gender')
    profile.phonenumber = data.get('phonenumber')
    db.session.commit()

    return jsonify({"message": "Profile has been updated"}), 200
