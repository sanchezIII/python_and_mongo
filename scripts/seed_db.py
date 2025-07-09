#!/usr/bin/env python
"""Database seeding script for loading sample data."""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from repositories.mongo_client import MongoClient
from models.customer import Customer
from models.product import Product
from services.subscription_service import SubscriptionService


def create_sample_customers():
    """Create sample customers."""
    customers = [
        {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'address': '123 Main St',
            'city': 'New York',
            'country': 'USA',
            'postal_code': '10001',
            'status': 'active'
        },
        {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1234567891',
            'address': '456 Oak Ave',
            'city': 'Los Angeles',
            'country': 'USA',
            'postal_code': '90210',
            'status': 'active'
        },
        {
            'name': 'Bob Johnson',
            'email': 'bob.johnson@example.com',
            'phone': '+1234567892',
            'address': '789 Pine Rd',
            'city': 'Chicago',
            'country': 'USA',
            'postal_code': '60601',
            'status': 'active'
        },
        {
            'name': 'Alice Brown',
            'email': 'alice.brown@example.com',
            'phone': '+1234567893',
            'address': '321 Elm St',
            'city': 'Houston',
            'country': 'USA',
            'postal_code': '77001',
            'status': 'inactive'
        },
        {
            'name': 'Charlie Wilson',
            'email': 'charlie.wilson@example.com',
            'phone': '+1234567894',
            'address': '654 Maple Dr',
            'city': 'Phoenix',
            'country': 'USA',
            'postal_code': '85001',
            'status': 'active'
        }
    ]
    
    return customers


def create_sample_products():
    """Create sample products."""
    products = [
        {
            'name': 'Basic Plan',
            'description': 'Basic subscription plan with essential features',
            'price': Decimal('9.99'),
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'trial_period_days': 7,
            'features': ['Basic Support', 'Limited Storage', 'Basic Analytics'],
            'is_active': True
        },
        {
            'name': 'Premium Plan',
            'description': 'Premium subscription plan with advanced features',
            'price': Decimal('29.99'),
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'trial_period_days': 14,
            'features': ['Priority Support', 'Unlimited Storage', 'Advanced Analytics', 'API Access'],
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
        },
        {
            'name': 'Pro Plan',
            'description': 'Professional subscription plan for businesses',
            'price': Decimal('99.99'),
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'trial_period_days': 30,
            'features': ['24/7 Support', 'Unlimited Everything', 'Custom Integration', 'White Label'],
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
        },
        {
            'name': 'Annual Basic',
            'description': 'Basic plan with annual billing',
            'price': Decimal('99.99'),
            'currency': 'USD',
            'billing_cycle': 'yearly',
            'trial_period_days': 7,
            'features': ['Basic Support', 'Limited Storage', 'Basic Analytics'],
            'is_active': True
        },
        {
            'name': 'Enterprise Plan',
            'description': 'Enterprise plan for large organizations',
            'price': Decimal('299.99'),
            'currency': 'USD',
            'billing_cycle': 'monthly',
            'trial_period_days': 30,
            'features': ['Dedicated Support', 'Custom Solutions', 'Enterprise Security', 'SLA'],
            'is_active': False
        }
    ]
    
    return products


def create_sample_subscriptions(customer_ids, product_ids):
    """Create sample subscriptions."""
    subscriptions = []
    
    # Create various subscription scenarios
    now = datetime.utcnow()
    
    # Active subscriptions
    subscriptions.append({
        'customer_id': customer_ids[0],
        'product_id': product_ids[0],
        'status': 'active',
        'amount': 9.99,
        'currency': 'USD',
        'billing_cycle': 'monthly',
        'start_date': now - timedelta(days=30),
        'custom_settings': {
            'topBarColor': '#ff0000',
            'topBarBackgroundColor': '#000000',
            'positionIndex': 1,
            'defaultLang': 'es'
        },
        'metadata': {'source': 'web', 'campaign': 'spring2024'}
    })
    
    subscriptions.append({
        'customer_id': customer_ids[1],
        'product_id': product_ids[1],
        'status': 'active',
        'amount': 29.99,
        'currency': 'USD',
        'billing_cycle': 'monthly',
        'start_date': now - timedelta(days=15),
        'custom_settings': {
            'topBarColor': '#00ff00',
            'topBarBackgroundColor': '#ffffff',
            'topBarButtonBackgroundColor': '#0000ff',
            'positionIndex': 0,
            'defaultLang': 'fr'
        },
        'metadata': {'source': 'mobile', 'referrer': 'friend'}
    })
    
    subscriptions.append({
        'customer_id': customer_ids[2],
        'product_id': product_ids[2],
        'status': 'active',
        'amount': 99.99,
        'currency': 'USD',
        'billing_cycle': 'monthly',
        'start_date': now - timedelta(days=45),
        'custom_settings': {
            'topBarColor': '#ffffff',
            'topBarBackgroundColor': '#333333',
            'topBarButtonBackgroundColor': '#007bff',
            'positionIndex': 2,
            'defaultLang': 'en'
        },
        'metadata': {'source': 'sales', 'account_manager': 'John Sales'}
    })
    
    # Trial subscription (no custom settings - will use product defaults)
    subscriptions.append({
        'customer_id': customer_ids[3],
        'product_id': product_ids[1],
        'status': 'trial',
        'amount': 0.00,
        'currency': 'USD',
        'billing_cycle': 'monthly',
        'start_date': now - timedelta(days=5),
        'trial_end_date': now + timedelta(days=9),
        'metadata': {'source': 'web', 'trial_type': 'free'}
    })
    
    # Canceled subscription (with partial custom settings)
    subscriptions.append({
        'customer_id': customer_ids[4],
        'product_id': product_ids[0],
        'status': 'canceled',
        'amount': 9.99,
        'currency': 'USD',
        'billing_cycle': 'monthly',
        'start_date': now - timedelta(days=60),
        'canceled_at': now - timedelta(days=10),
        'custom_settings': {
            'defaultLang': 'de',
            'positionIndex': 3
        },
        'metadata': {'source': 'web', 'cancellation_reason': 'price'}
    })
    
    # Expired subscription (no custom settings)
    subscriptions.append({
        'customer_id': customer_ids[0],
        'product_id': product_ids[3],
        'status': 'expired',
        'amount': 99.99,
        'currency': 'USD',
        'billing_cycle': 'yearly',
        'start_date': now - timedelta(days=400),
        'metadata': {'source': 'web', 'promotion': 'annual_discount'}
    })
    
    return subscriptions


def seed_database():
    """Seed the database with sample data."""
    print("Starting database seeding...")
    
    # Configuration
    config = {
        'MONGODB_URI': os.getenv('MONGODB_URI', 'mongodb://localhost:27017/flask_db'),
        'MONGODB_DATABASE': os.getenv('MONGODB_DATABASE', 'flask_db')
    }
    
    try:
        # Initialize MongoDB client
        mongo_client = MongoClient(config)
        print(f"Connected to database: {config['MONGODB_DATABASE']}")
        
        # Clear existing data (optional)
        clear_existing = input("Clear existing data? (y/N): ").lower() == 'y'
        if clear_existing:
            mongo_client.get_collection('customers').delete_many({})
            mongo_client.get_collection('products').delete_many({})
            mongo_client.get_collection('subscriptions').delete_many({})
            print("Existing data cleared.")
        
        # Create customers
        print("Creating customers...")
        customers_data = create_sample_customers()
        customers_collection = mongo_client.get_collection('customers')
        
        customer_ids = []
        for customer_data in customers_data:
            customer = Customer.from_dict(customer_data)
            customer_doc = customer.to_dict()
            customer_doc.pop('_id', None)
            
            result = customers_collection.insert_one(customer_doc)
            customer_ids.append(result.inserted_id)
            print(f"Created customer: {customer_data['name']}")
        
        # Create products
        print("Creating products...")
        products_data = create_sample_products()
        products_collection = mongo_client.get_collection('products')
        
        product_ids = []
        for product_data in products_data:
            product = Product.from_dict(product_data)
            product_doc = product.to_dict()
            product_doc.pop('_id', None)
            
            result = products_collection.insert_one(product_doc)
            product_ids.append(result.inserted_id)
            print(f"Created product: {product_data['name']}")
        
        # Create subscriptions
        print("Creating subscriptions...")
        subscriptions_data = create_sample_subscriptions(customer_ids, product_ids)
        subscription_service = SubscriptionService(mongo_client)
        
        for i, subscription_data in enumerate(subscriptions_data):
            subscription_data['customer_id'] = str(subscription_data['customer_id'])
            subscription_data['product_id'] = str(subscription_data['product_id'])
            
            try:
                # Use the new subscribe method for the first subscription to demonstrate enhanced features
                if i == 0:
                    print(f"Creating enhanced subscription using subscribe method...")
                    # Convert ObjectIds back for subscribe method
                    subscription_data['customer_id'] = ObjectId(subscription_data['customer_id'])
                    subscription_data['product_id'] = ObjectId(subscription_data['product_id'])
                    
                    # Add enhanced features for demonstration
                    subscription_data['apply_product_defaults'] = True
                    subscription_data['auto_renew'] = True
                    # Remove amount, currency, billing_cycle to demonstrate inheritance
                    enhanced_data = {k: v for k, v in subscription_data.items() 
                                   if k not in ['amount', 'currency', 'billing_cycle']}
                    
                    subscription = subscription_service.subscribe(enhanced_data)
                    print(f"Created enhanced subscription with product info: {subscription.get('product_info', {}).get('name', 'Unknown')}")
                else:
                    subscription = subscription_service.create_subscription(subscription_data)
                    print(f"Created subscription for customer: {subscription_data['customer_id']}")
            except Exception as e:
                print(f"Error creating subscription: {e}")
        
        # Create indexes
        print("Creating database indexes...")
        mongo_client.create_indexes()
        
        print("Database seeding completed successfully!")
        
        # Display summary
        customers_count = customers_collection.count_documents({})
        products_count = products_collection.count_documents({})
        subscriptions_count = mongo_client.get_collection('subscriptions').count_documents({})
        
        print(f"\nSummary:")
        print(f"- Customers: {customers_count}")
        print(f"- Products: {products_count}")
        print(f"- Subscriptions: {subscriptions_count}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        if 'mongo_client' in locals():
            mongo_client.close()


if __name__ == "__main__":
    seed_database() 