"""Development configuration settings."""

import os
from .default import Config


class DevelopmentConfig(Config):
    """Development configuration class."""
    
    DEBUG = True
    DEVELOPMENT = True
    
    # Database settings for development
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/flask_db_dev')
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'flask_db_dev')
    
    # Logging settings for development
    LOG_LEVEL = 'DEBUG'
    
    # CORS settings for development (more permissive)
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080', 'http://127.0.0.1:3000']
    
    # Rate limiting for development (more permissive)
    RATE_LIMIT = 1000
    
    # Email settings for development (use console backend)
    MAIL_SUPPRESS_SEND = True
    MAIL_DEBUG = True
    
    @staticmethod
    def init_app(app):
        """Initialize the Flask application with development configuration."""
        Config.init_app(app)
        
        # Development-specific initialization
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Enable Flask development features
        app.config['EXPLAIN_TEMPLATE_LOADING'] = True 