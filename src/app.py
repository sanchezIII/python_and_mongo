"""Flask application entry point."""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from repositories.mongo_client import MongoClient
from routes.customers import customers_bp
from routes.subscriptions import subscriptions_bp
from routes.products import products_bp
from utils.auth import validate_api_key


def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'production':
        from config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'development':
        from config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    else:
        from config.default import Config
        app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    
    # Initialize MongoDB client
    mongo_client = MongoClient(app.config)
    app.mongo = mongo_client
    
    # API Authentication middleware
    @app.before_request
    def require_api_key():
        """Require API key for all /api/ routes except OPTIONS (CORS preflight)."""
        from flask import request
        
        # Skip authentication for CORS preflight requests
        if request.method == 'OPTIONS':
            return None
            
        # Apply authentication only to API routes
        if request.path.startswith('/api/'):
            auth_error = validate_api_key()
            if auth_error:
                return auth_error
    
    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix=f"{app.config['API_PREFIX']}")
    app.register_blueprint(subscriptions_bp, url_prefix=f"{app.config['API_PREFIX']}")
    app.register_blueprint(products_bp, url_prefix=f"{app.config['API_PREFIX']}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        try:
            # Check database connection
            mongo_client.get_database().command('ping')
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'version': app.config.get('API_VERSION', 'v1')
            }), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }), 503
    
    # Root endpoint
    @app.route('/')
    def index():
        """Root endpoint."""
        return jsonify({
            'message': 'Flask + MongoDB API',
            'version': app.config.get('API_VERSION', 'v1'),
            'endpoints': {
                'customers': f"{app.config['API_PREFIX']}/customers",
                'subscriptions': f"{app.config['API_PREFIX']}/subscriptions",
                'products': f"{app.config['API_PREFIX']}/products",
                'health': '/health'
            }
        })
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')
    else:
        # Configure console logging for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        console_handler.setLevel(logging.INFO)
        
        # Configure root logger for all modules
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
        
        # Also configure app logger
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup (development mode)')
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(
        host=host,
        port=port,
        debug=app.config.get('DEBUG', False)
    ) 