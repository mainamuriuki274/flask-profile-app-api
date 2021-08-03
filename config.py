import decouple
import os


# config.py
class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = decouple.config('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_EXTENSIONS = ['data:image/png;base64', 'data:image/jpg;base64', 'data:image/jpeg;base64']
    MAX_CONTENT_LENGTH = 1024 * 1024
    

class ProductionConfig(Config):
    db_path = os.path.abspath(os.getcwd()) + decouple.config('DATABASE_URL')
    db_uri = 'sqlite:///{}'.format(db_path)
    SQLALCHEMY_DATABASE_URI = db_uri
    UPLOAD_PATH = os.path.dirname(os.getcwd()) + "/app/static/images/"


class DevelopmentConfig(Config):
    DEBUG = True
    db_path = os.path.abspath(os.getcwd()) + decouple.config('DEVELOPMENT_DATABASE_URL')
    db_uri = 'sqlite:///{}'.format(db_path)
    SQLALCHEMY_DATABASE_URI = db_uri


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    UPLOAD_PATH = os.path.abspath(os.getcwd()) + "/app/static/test_images/"

