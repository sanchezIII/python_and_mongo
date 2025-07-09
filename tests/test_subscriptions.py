"""Test cases for subscription models and services."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from unittest.mock import Mock, patch
from src.services.subscription_service import SubscriptionService
from src.models.subscription import Subscription


class TestSubscriptionService:
    """Test SubscriptionService business logic."""

    def test_create_subscription_validates_customer(self, mock_mongo_client):
        """Test subscription creation validates customer exists."""
        service = SubscriptionService(mock_mongo_client)
        
        # Mock customer not found
        service.customers_collection.find_one.return_value = None
        
        with pytest.raises(ValueError, match="Customer not found"):
            service.create_subscription({
                'customer_id': str(ObjectId()),
                'product_id': str(ObjectId()),
                'amount': 29.99,
                'currency': 'USD',
                'billing_cycle': 'monthly'
            })

    def test_cancel_subscription_already_canceled(self, mock_mongo_client):
        """Test canceling an already canceled subscription."""
        service = SubscriptionService(mock_mongo_client)
        subscription_id = str(ObjectId())
        
        # Mock existing canceled subscription
        canceled_subscription = {
            '_id': ObjectId(subscription_id),
            'customer_id': ObjectId(),
            'status': 'canceled',
            'amount': Decimal('29.99'),
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + timedelta(days=30),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'custom_settings': {},
            'metadata': {}
        }
        
        service.subscriptions_collection.find_one.return_value = canceled_subscription
        
        with pytest.raises(ValueError, match="already canceled"):
            service.cancel_subscription(subscription_id)

    def test_calculate_end_date_monthly(self, mock_mongo_client):
        """Test end date calculation for monthly billing cycle."""
        service = SubscriptionService(mock_mongo_client)
        
        start_date = datetime(2023, 1, 1, 12, 0, 0)
        end_date = service._calculate_end_date(start_date, 'monthly')
        
        expected_end_date = start_date + timedelta(days=30)
        assert end_date == expected_end_date 