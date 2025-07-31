import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False
    ERROR_INCLUDE_MESSAGE = False
    BCRYPT_LOG_ROUNDS = 12
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    ERROR_INCLUDE_MESSAGE = False
    BCRYPT_LOG_ROUNDS = 12
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'adminpassword')
    REGULAR_USER_EMAIL = 'user@example.com'
    REGULAR_USER_PASSWORD = 'password'

    DELETED_USER_EMAIL = 'deleted@example.com'
    DELETED_USER_PASSWORD = 'password'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'adminpassword'
    REGULAR_USER_EMAIL = 'user@example.com'
    REGULAR_USER_PASSWORD = 'password'

    DELETED_USER_EMAIL = 'deleted@example.com'
    DELETED_USER_PASSWORD = 'password'


config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
