"""Production configuration settings."""

import os
from .default import Config


class ProductionConfig(Config):
    """Production configuration class."""
    
    DEBUG = False
    TESTING = False
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Database settings for production
    MONGODB_URI = os.environ.get('MONGODB_URI')
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable must be set in production")
    
    # Logging settings for production
    LOG_LEVEL = 'WARNING'
    
    # CORS settings for production (more restrictive)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    if not CORS_ORIGINS or CORS_ORIGINS == ['']:
        raise ValueError("CORS_ORIGINS environment variable must be set in production")
    
    # Rate limiting for production (more restrictive)
    RATE_LIMIT = int(os.environ.get('RATE_LIMIT', 50))
    
    # SSL settings
    PREFERRED_URL_SCHEME = 'https'
    
    # Session settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # JWT settings for production
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable must be set in production")
    
    @staticmethod
    def init_app(app):
        """Initialize the Flask application with production configuration."""
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Set up file logging
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = RotatingFileHandler(
            'logs/app.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup') 