"""Test configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from bson import ObjectId

from src.app import create_app
from src.repositories.mongo_client import MongoClient


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['MONGODB_URI'] = 'mongodb://localhost:27017/test_flask_db'
    
    # Mock MongoDB client for testing
    with patch('src.repositories.mongo_client.MongoClient') as mock_mongo:
        mock_mongo_instance = Mock()
        mock_mongo.return_value = mock_mongo_instance
        
        # Mock collections
        mock_mongo_instance.get_collection.return_value = Mock()
        mock_mongo_instance.get_database.return_value = Mock()
        mock_mongo_instance.ping.return_value = True
        
        app.mongo = mock_mongo_instance
        yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_mongo_client():
    """Mock MongoDB client."""
    with patch('src.repositories.mongo_client.MongoClient') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Mock collection methods
        mock_collection = Mock()
        mock_instance.get_collection.return_value = mock_collection
        mock_instance.get_database.return_value = Mock()
        mock_instance.ping.return_value = True
        
        # Add collection properties for subscription service
        mock_instance.customers_collection = Mock()
        mock_instance.products_collection = Mock()
        mock_instance.subscriptions_collection = Mock()
        
        yield mock_instance


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890',
        'address': '123 Main St',
        'city': 'New York',
        'country': 'USA',
        'postal_code': '10001',
        'status': 'active'
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        'name': 'Premium Plan',
        'description': 'Premium subscription plan',
        'price': 29.99,
        'currency': 'USD',
        'billing_cycle': 'monthly',
        'trial_period_days': 7,
        'features': ['Feature 1', 'Feature 2'],
        'is_active': True,
        'customizable': True,
        'customizable_fields': [
            'topBarColor',
            'topBarBackgroundColor',
            'topBarButtonBackgroundColor',
            'positionIndex',
            'defaultLang'
        ],
        'default_settings': {
            'topBarColor': '#ffffff',
            'topBarBackgroundColor': '#000000',
            'topBarButtonBackgroundColor': '#000000',
            'positionIndex': 0,
            'defaultLang': 'en'
        }
    } 