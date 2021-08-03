from app import app
from app.models import db
import base64
import pytest
import json
import os
import sys
from config import TestingConfig


token_data = {
    'token': ''
}


@pytest.fixture(scope="module")
def client():
    app.config.from_object(TestingConfig)
    client = app.test_client()
    with app.app_context():
        db.create_all()
    yield client
    
    test_images_directory = app.config['UPLOAD_PATH']
    for img in os.listdir(test_images_directory):
        os.remove(os.path.join(test_images_directory, img))


def test_create_user(client):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'email': 'testUser@gmail.com',
        'password': '1234567890'
    }
    url = '/api/v1/user'
    response = client.post(url, data=json.dumps(data), headers=headers)
    response_data = response.json
    token_data['token'] = response_data.get('token')
    assert response.status_code == 201

def test_login(client):
    headers = {
        "Authorization" : "Basic %s" % base64.b64encode('testUser@gmail.com:1234567890'.encode()).decode()
        }
    url = '/api/v1/login'
    response = client.get(url, headers=headers)
    response_data = response.json
    token_data['token'] = response_data.get('token')
    assert response.status_code == 200

def test_update_email(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
        'x-access-token': token_data.get('token')
    }
    data = {
        'email': 'testUserUpdate@gmail.com',
    }
    url = '/api/v1/user/email'
    response = client.put(url, data=json.dumps(data), headers=headers)
    assert response.status_code == 200


def test_update_password(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
        'x-access-token': token_data.get('token')
    }
    data = {
        'password': '1234567890',
        'newPassword': 'updatedpassword',
    }
    url = '/api/v1/user/password'
    response = client.put(url, data=json.dumps(data), headers=headers)
    assert response.status_code == 200


def test_updated_login(client):
    headers = {
        "Authorization" : "Basic %s" % base64.b64encode('testUserUpdate@gmail.com:updatedpassword'.encode()).decode('UTF-8')
        }
    url = '/api/v1/login'
    response = client.get(url, headers=headers)
    response_data = response.json
    token_data['token'] = response_data.get('token')
    assert response.status_code == 200


def test_get_user(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
        'x-access-token': token_data.get('token')
    }
    url = '/api/v1/user'
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_get_email(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
    }
    url = '/api/v1/email/testUserUpdate@gmail.com'
    response = client.get(url, headers=headers)
    assert response.status_code == 409



def test_create_user_profile(client):
    with open(os.path.dirname(os.getcwd()) + '/tests/test_b64_img.txt') as img:
        b64_img = img.read()
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
        'x-access-token': token_data.get('token')
    }
    data = {
        'username': 'testUsername',
        'img': b64_img,
        'firstname': 'TestFirstname',
        'lastname': 'TestLastname',
        'dob': '2021-08-12',
        'gender': 'male',
        'phonenumber': '0714309092'
    }
    url = '/api/v1/profile'
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.status_code == 201


def test_get_username(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
    }
    url = '/api/v1/username/testUsername'
    response = client.get(url, headers=headers)
    assert response.status_code == 409


def test_get_phonenumber(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
    }
    url = '/api/v1/phonenumber/0714309092'
    response = client.get(url, headers=headers)
    assert response.status_code == 409


def test_delete_user(client):
    headers = {
        'Content-Type': 'application/json',
        'x-access-token': token_data.get('token')
    }
    data = {
        'password': 'updatedpassword'
    }
    url = '/api/v1/user'
    response = client.delete(url,data=json.dumps(data) ,headers=headers)
    assert response.status_code == 200