"""Test cases for customer models and functionality."""

import pytest
from datetime import datetime
from bson import ObjectId
from src.models.customer import Customer, customer_schema
from marshmallow import ValidationError


class TestCustomerModel:
    """Test Customer model functionality."""

    def test_customer_creation(self, sample_customer_data):
        """Test customer creation with valid data."""
        customer = Customer.from_dict(sample_customer_data)
        
        assert customer.name == sample_customer_data['name']
        assert customer.email == sample_customer_data['email']
        assert customer.phone == sample_customer_data['phone']
        assert customer.address == sample_customer_data['address']
        assert customer.city == sample_customer_data['city']
        assert customer.country == sample_customer_data['country']
        assert customer.postal_code == sample_customer_data['postal_code']
        assert customer.status == sample_customer_data['status']
        assert isinstance(customer.created_at, datetime)
        assert isinstance(customer.updated_at, datetime)

    def test_customer_to_dict(self, sample_customer_data):
        """Test customer serialization to dictionary."""
        customer = Customer.from_dict(sample_customer_data)
        customer._id = ObjectId()
        
        result = customer.to_dict()
        
        assert result['_id'] == customer._id
        assert result['name'] == customer.name
        assert result['email'] == customer.email
        assert result['phone'] == customer.phone
        assert result['address'] == customer.address
        assert result['city'] == customer.city
        assert result['country'] == customer.country
        assert result['postal_code'] == customer.postal_code
        assert result['status'] == customer.status
        assert isinstance(result['created_at'], datetime)
        assert isinstance(result['updated_at'], datetime)

    def test_customer_schema_validation(self, sample_customer_data):
        """Test customer schema validation with valid data."""
        result = customer_schema.load(sample_customer_data)
        
        assert isinstance(result, Customer)
        assert result.name == sample_customer_data['name']
        assert result.email == sample_customer_data['email']
        assert result.status == sample_customer_data['status'] 