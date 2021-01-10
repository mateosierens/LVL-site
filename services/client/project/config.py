# services/client/project/config.py

import os

class BaseConfig:
    """
    Base configuration
    """
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my_precious'

    # Configure application to store JWTs in cookies
    JWT_TOKEN_LOCATION = ['cookies']

    # Enable csrf double submit protection
    JWT_COOKIE_CSRF_PROTECT = False

    # Set the secret key to sign the JWTs with
    JWT_SECRET_KEY = '*^*(*&)(*)(*afafafaSDD47j\3yX R~X@H!jmM]Lwf/,?KT'

class DevelopmentConfig(BaseConfig):
    """
    Development configuration
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(BaseConfig):
    """
    Testing Configuration
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')