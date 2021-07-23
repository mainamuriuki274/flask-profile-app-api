# config.py
class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "Th1s%#1s&my*!S3cr3t%&K3y"
    UPLOAD_PATH = "app/static/profile_photos/"
    DATABASE_URL = 'sqlite:///app/db/prometheus.db'
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
