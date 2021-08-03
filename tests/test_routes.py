from app import create_app as app
from app.models import db
import pytest
import json

token = None


@pytest.fixture
def client():
    app.config.from_object("config.TestingConfig")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    client = app.test_client()
    with app.app_context():
        db.create_all()
    yield client


def test_create_user(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {
        'email': 'testUser@gmail.com',
        'password': '1234567890'
    }
    url = '/api/v1/user'
    response = client.post(url, data=json.dumps(data), headers=headers)
    token = response.json().token
    assert response.content_type == mimetype
    assert response.status_code == 201


def test_login(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {
        'email': 'testUser@gmail.com',
        'password': '1234567890'
    }
    url = '/api/v1/user'
    response = client.get(url, data=json.dumps(data), headers=headers)
    token = response.json().token
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_update_email(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
        'x-access-token': token
    }
    data = {
        'email': 'testUserUpdate@gmail.com',
    }
    url = '/api/v1/email'
    response = client.get(url, data=json.dumps(data), headers=headers)

    assert response.content_type == mimetype
    assert response.status_code == 200


def test_update_password(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
        'x-access-token': token
    }
    data = {
        'password': 'updatedpassword',
    }
    url = '/api/v1/password'
    response = client.get(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_updated_login(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {
        'email': 'testUserUpdate@gmail.com',
        'password': 'updatedpassword'
    }
    url = '/api/v1/user'
    response = client.get(url, data=json.dumps(data), headers=headers)
    token = response.json().token
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_get_user(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
        'x-access-token': token
    }
    url = '/api/v1/user'
    response = client.get(url, headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_get_users(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
        'x-access-token': token
    }
    url = '/api/v1/users'
    response = client.get(url, headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_get_email(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
    }
    url = '/api/v1/email/testUser@gmail.com'
    response = client.get(url, headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 409


def test_get_username(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
    }
    url = '/api/v1/username/testUsername.com'
    response = client.get(url, headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 409


def test_get_phonenumber(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
    }
    url = '/api/v1/username/0714309092'
    response = client.get(url, headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 409


def test_delete_user(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
    }
    url = '/api/v1/user'
    response = client.delete(url, headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_create_user_profile(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {
        'email': 'testUser@gmail.com',
        'password': '1234567890'
    }
    url = '/api/v1/user'
    response = client.post(url, data=json.dumps(data), headers=headers)
    token = response.json().token
    assert response.content_type == mimetype
    assert response.status_code == 201
