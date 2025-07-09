"""Test cases for product models and functionality."""

import pytest
from datetime import datetime
from decimal import Decimal
from bson import ObjectId
from src.models.product import Product, product_schema


class TestProductModel:
    """Test Product model functionality."""

    def test_product_creation_with_customization(self, sample_product_data):
        """Test product creation with customization features."""
        product = Product.from_dict(sample_product_data)
        
        assert product.name == sample_product_data['name']
        assert product.description == sample_product_data['description']
        assert product.price == Decimal(str(sample_product_data['price']))
        assert product.currency == sample_product_data['currency']
        assert product.billing_cycle == sample_product_data['billing_cycle']
        assert product.trial_period_days == sample_product_data['trial_period_days']
        assert product.features == sample_product_data['features']
        assert product.is_active == sample_product_data['is_active']
        assert product.customizable == sample_product_data['customizable']
        assert product.customizable_fields == sample_product_data['customizable_fields']
        assert product.default_settings == sample_product_data['default_settings']
        assert isinstance(product.created_at, datetime)
        assert isinstance(product.updated_at, datetime)

    def test_product_to_dict(self, sample_product_data):
        """Test product serialization to dictionary."""
        product = Product.from_dict(sample_product_data)
        product._id = ObjectId()
        
        result = product.to_dict()
        
        assert result['_id'] == product._id
        assert result['name'] == product.name
        assert result['description'] == product.description
        assert result['price'] == float(product.price)
        assert result['currency'] == product.currency
        assert result['billing_cycle'] == product.billing_cycle
        assert result['trial_period_days'] == product.trial_period_days
        assert result['features'] == product.features
        assert result['is_active'] == product.is_active
        assert result['customizable'] == product.customizable
        assert result['customizable_fields'] == product.customizable_fields
        assert result['default_settings'] == product.default_settings
        assert isinstance(result['created_at'], datetime)
        assert isinstance(result['updated_at'], datetime)

    def test_product_monthly_price_calculation(self, sample_product_data):
        """Test monthly price calculation for different billing cycles."""
        # Test monthly product
        monthly_data = sample_product_data.copy()
        monthly_data['billing_cycle'] = 'monthly'
        monthly_data['price'] = 30.0
        
        monthly_product = Product.from_dict(monthly_data)
        assert monthly_product.get_monthly_price() == Decimal('30.0')
        
        # Test yearly product
        yearly_data = sample_product_data.copy()
        yearly_data['billing_cycle'] = 'yearly'
        yearly_data['price'] = 360.0
        
        yearly_product = Product.from_dict(yearly_data)
        # Yearly price / 12 months = monthly equivalent
        assert yearly_product.get_monthly_price() == Decimal('30.0')

    def test_product_update(self, sample_product_data):
        """Test product update functionality."""
        product = Product.from_dict(sample_product_data)
        original_updated_at = product.updated_at
        
        # Test updating basic fields
        product.update(
            name='Updated Product Name',
            price=Decimal('49.99'),
            is_active=False
        )
        
        assert product.name == 'Updated Product Name'
        assert product.price == Decimal('49.99')
        assert product.is_active == False
        assert product.updated_at > original_updated_at 