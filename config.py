from decouple import config


# config.py
class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = config('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL')
    UPLOAD_PATH = "/home/maina-muriuki/Documents/flask-profile-app-api/app/static/images/"
    UPLOAD_EXTENSIONS = ['.jpg', '.png']
    MAX_CONTENT_LENGTH = 1024 * 1024


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    # Enable Flask's debugging features. Should be False in production
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
