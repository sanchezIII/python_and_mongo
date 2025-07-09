#!/usr/bin/env python
"""
Example script to test the new POST /api/subscribe endpoint.

This script demonstrates all the advanced features of the subscribe endpoint:
- Product property inheritance
- Custom settings with product defaults
- Specific end dates
- Trial management
- Enhanced validation

Run this after seeding the database with sample data.
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:5001/api"

def test_subscribe_endpoint():
    """Test the subscribe endpoint with various scenarios."""
    
    print("🧪 Testing POST /api/subscribe endpoint\n")
    
    # Get sample customer and product IDs (from seeded data)
    print("1️⃣ Getting sample customer and product...")
    
    # Get customers
    customers_response = requests.get(f"{BASE_URL}/customers")
    if customers_response.status_code == 200:
        customers = customers_response.json()['customers']
        customer_id = customers[0]['_id'] if customers else None
        print(f"   Using customer: {customers[0]['name']} ({customer_id})")
    else:
        print("❌ Failed to get customers")
        return
    
    # Get products (preferably customizable ones)
    products_response = requests.get(f"{BASE_URL}/products?customizable=true")
    if products_response.status_code == 200:
        products = products_response.json()['products']
        product = products[0] if products else None
        product_id = product['_id'] if product else None
        print(f"   Using product: {product['name']} ({product_id})")
        print(f"   Product price: {product['price']} {product['currency']}")
        print(f"   Customizable: {product.get('customizable', False)}")
        print(f"   Default settings: {json.dumps(product.get('default_settings', {}), indent=6)}")
    else:
        print("❌ Failed to get products")
        return
    
    if not customer_id or not product_id:
        print("❌ Missing customer or product data")
        return
    
    print("\n" + "="*60)
    
    # Test 1: Minimal subscription (inherits product properties)
    print("\n2️⃣ TEST 1: Minimal subscription (inherits all product properties)")
    minimal_data = {
        "customer_id": customer_id,
        "product_id": product_id
    }
    
    response = requests.post(f"{BASE_URL}/subscribe", json=minimal_data)
    if response.status_code == 201:
        subscription = response.json()
        print("✅ SUCCESS - Minimal subscription created:")
        print(f"   ID: {subscription['_id']}")
        print(f"   Amount: {subscription['amount']} {subscription['currency']} (inherited from product)")
        print(f"   Billing: {subscription['billing_cycle']} (inherited from product)")
        print(f"   Status: {subscription['status']}")
        print(f"   Custom settings: {json.dumps(subscription.get('custom_settings', {}), indent=6)}")
        print(f"   Product info: {subscription.get('product_info', {}).get('name')}")
        
        # Save for cleanup
        minimal_subscription_id = subscription['_id']
    else:
        print(f"❌ FAILED - {response.status_code}: {response.text}")
        return
    
    print("\n" + "="*60)
    
    # Test 2: Custom subscription with specific settings and end date
    print("\n3️⃣ TEST 2: Custom subscription with settings and specific end date")
    
    # Calculate a specific end date (6 months from now)
    end_date = (datetime.utcnow() + timedelta(days=180)).isoformat() + "Z"
    
    custom_data = {
        "customer_id": customer_id,
        "product_id": product_id,
        "custom_settings": {
            "topBarColor": "#ff0000",
            "topBarBackgroundColor": "#00ff00",
            "positionIndex": 5,
            "defaultLang": "es"
        },
        "end_date": end_date,
        "metadata": {
            "source": "api_test",
            "campaign": "demo_test",
            "notes": "Testing custom settings and end date"
        }
    }
    
    response = requests.post(f"{BASE_URL}/subscribe", json=custom_data)
    if response.status_code == 201:
        subscription = response.json()
        print("✅ SUCCESS - Custom subscription created:")
        print(f"   ID: {subscription['_id']}")
        print(f"   Custom end date: {subscription['end_date']}")
        print(f"   Custom settings: {json.dumps(subscription.get('custom_settings', {}), indent=6)}")
        print(f"   Metadata: {json.dumps(subscription.get('metadata', {}), indent=6)}")
        
        # Save for cleanup
        custom_subscription_id = subscription['_id']
    else:
        print(f"❌ FAILED - {response.status_code}: {response.text}")
        custom_subscription_id = None
    
    print("\n" + "="*60)
    
    # Test 3: Subscription overriding product properties
    print("\n4️⃣ TEST 3: Subscription overriding product properties")
    
    override_data = {
        "customer_id": customer_id,
        "product_id": product_id,
        "amount": 19.99,  # Override product price
        "currency": "EUR",  # Override product currency  
        "billing_cycle": "yearly",  # Override product billing cycle
        "custom_settings": {
            "topBarColor": "#0000ff"
        },
        "apply_product_defaults": False,  # Don't apply product defaults
        "auto_renew": False,
        "metadata": {
            "override_test": True,
            "original_price": product['price']
        }
    }
    
    response = requests.post(f"{BASE_URL}/subscribe", json=override_data)
    if response.status_code == 201:
        subscription = response.json()
        print("✅ SUCCESS - Override subscription created:")
        print(f"   ID: {subscription['_id']}")
        print(f"   Amount: {subscription['amount']} {subscription['currency']} (overridden)")
        print(f"   Billing: {subscription['billing_cycle']} (overridden)")
        print(f"   Custom settings: {json.dumps(subscription.get('custom_settings', {}), indent=6)}")
        print(f"   Auto-renew: {subscription.get('metadata', {}).get('auto_renew', 'not set')}")
        
        # Save for cleanup
        override_subscription_id = subscription['_id']
    else:
        print(f"❌ FAILED - {response.status_code}: {response.text}")
        override_subscription_id = None
    
    print("\n" + "="*60)
    
    # Test 4: Error case - Duplicate subscription
    print("\n5️⃣ TEST 4: Error handling - Duplicate subscription")
    
    duplicate_data = {
        "customer_id": customer_id,
        "product_id": product_id
    }
    
    response = requests.post(f"{BASE_URL}/subscribe", json=duplicate_data)
    if response.status_code == 400:
        error = response.json()
        print("✅ SUCCESS - Duplicate subscription correctly rejected:")
        print(f"   Error: {error.get('error')}")
    else:
        print(f"❌ UNEXPECTED - Expected 400 but got {response.status_code}: {response.text}")
    
    print("\n" + "="*60)
    
    # Test 5: Test GetSettings on custom subscription
    if 'custom_subscription_id' in locals() and custom_subscription_id:
        print(f"\n6️⃣ TEST 5: Testing GetSettings on custom subscription")
        
        settings_response = requests.get(f"{BASE_URL}/subscriptions/{custom_subscription_id}/settings")
        if settings_response.status_code == 200:
            settings = settings_response.json()
            print("✅ SUCCESS - Retrieved subscription settings:")
            print(f"   Product defaults: {json.dumps(settings.get('product_defaults', {}), indent=6)}")
            print(f"   Custom settings: {json.dumps(settings.get('custom_settings', {}), indent=6)}")
            print(f"   Effective settings: {json.dumps(settings.get('effective_settings', {}), indent=6)}")
        else:
            print(f"❌ FAILED - {settings_response.status_code}: {settings_response.text}")
    
    print("\n" + "="*60)
    print("\n🎉 Testing completed!")
    
    # Cleanup (cancel created subscriptions)
    print("\n🧹 Cleaning up test subscriptions...")
    for sub_id, name in [
        (minimal_subscription_id, "minimal"),
        (custom_subscription_id, "custom"), 
        (override_subscription_id, "override")
    ]:
        if 'sub_id' in locals() and sub_id:
            cancel_response = requests.post(f"{BASE_URL}/subscriptions/{sub_id}/cancel")
            if cancel_response.status_code == 200:
                print(f"   ✅ Canceled {name} subscription ({sub_id})")
            else:
                print(f"   ❌ Failed to cancel {name} subscription: {cancel_response.text}")


if __name__ == "__main__":
    try:
        test_subscribe_endpoint()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API. Make sure the Flask app is running on localhost:5001")
    except Exception as e:
        print(f"❌ ERROR: {e}") 