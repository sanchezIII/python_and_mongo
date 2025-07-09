"""Default configuration settings for the Flask application."""

import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP = os.environ.get('FLASK_APP', 'src/app.py')
    
    # Database settings
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/flask_db')
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'flask_db')
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
    
    # API settings
    API_PREFIX = os.environ.get('API_PREFIX', '/api')
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get(
        'LOG_FORMAT', 
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Rate limiting
    RATE_LIMIT = int(os.environ.get('RATE_LIMIT', 100))
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # External services
    EXTERNAL_API_URL = os.environ.get('EXTERNAL_API_URL')
    EXTERNAL_API_KEY = os.environ.get('EXTERNAL_API_KEY')
    
    # Testing
    TESTING = os.environ.get('TESTING', 'False').lower() in ('true', '1', 'yes')
    TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL', 'mongodb://localhost:27017/test_flask_db')

    @staticmethod
    def init_app(app):
        """Initialize the Flask application with configuration."""
        pass 