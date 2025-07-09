"""Subscription service with business logic."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from bson import ObjectId
from decimal import Decimal

from repositories.mongo_client import MongoClient
from models.subscription import Subscription, subscription_schema


class SubscriptionService:
    """Service for managing subscription business logic."""
    
    def __init__(self, mongo_client: MongoClient):
        """Initialize subscription service."""
        self.mongo = mongo_client
        self.subscriptions_collection = mongo_client.get_collection('subscriptions')
        self.customers_collection = mongo_client.get_collection('customers')
        self.products_collection = mongo_client.get_collection('products')
    
    def create_subscription(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new subscription with customization support."""
        # Validate customer exists
        customer_id = ObjectId(data['customer_id'])
        customer = self.customers_collection.find_one({'_id': customer_id})
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate product if provided and get customization defaults
        product = None
        if 'product_id' in data and data['product_id']:
            product_id = ObjectId(data['product_id'])
            product = self.products_collection.find_one({'_id': product_id})
            if not product:
                raise ValueError("Product not found")
        
        # Create subscription using the model
        subscription_data = {
            'customer_id': customer_id,
            'product_id': ObjectId(data['product_id']) if data.get('product_id') else None,
            'amount': Decimal(str(data.get('amount', '0.00'))),
            'currency': data.get('currency', 'USD'),
            'billing_cycle': data.get('billing_cycle', 'monthly'),
            'status': data.get('status', 'active'),
            'custom_settings': data.get('custom_settings', {}),
            'start_date': data.get('start_date', datetime.utcnow()),
            'trial_end_date': data.get('trial_end_date'),
            'metadata': data.get('metadata', {})
        }
        
        # Calculate end date
        subscription_data['end_date'] = self._calculate_end_date(
            subscription_data['start_date'],
            subscription_data['billing_cycle']
        )
        
        # Create subscription model instance
        subscription = Subscription.from_dict(subscription_data)
        
        # Apply product default settings if product is customizable
        if product and product.get('customizable', False):
            default_settings = product.get('default_settings', {})
            if default_settings:
                subscription.apply_product_defaults(default_settings)
        
        # Convert to dict for database insertion
        subscription_doc = subscription.to_dict()
        subscription_doc.pop('_id', None)  # Remove _id if present
        
        # Insert subscription
        result = self.subscriptions_collection.insert_one(subscription_doc)
        
        # Return created subscription with proper formatting
        subscription._id = result.inserted_id
        return self._format_subscription_response(subscription)
    
    def update_subscription(self, subscription_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing subscription."""
        oid = ObjectId(subscription_id)
        
        # Get current subscription
        subscription_doc = self.subscriptions_collection.find_one({'_id': oid})
        if not subscription_doc:
            raise ValueError("Subscription not found")
        
        # Create subscription model instance
        subscription = Subscription.from_dict(subscription_doc)
        
        # Prepare update data
        update_data = {}
        
        # Update allowed fields
        allowed_fields = ['status', 'amount', 'currency', 'billing_cycle', 'custom_settings', 'metadata']
        for field in allowed_fields:
            if field in data:
                if field == 'amount':
                    subscription.amount = Decimal(str(data[field]))
                    update_data[field] = float(subscription.amount)
                elif field == 'custom_settings':
                    subscription.custom_settings = data[field]
                    update_data[field] = subscription.custom_settings
                else:
                    setattr(subscription, field, data[field])
                    update_data[field] = data[field]
        
        # Update end date if billing cycle changed
        if 'billing_cycle' in data:
            subscription.end_date = self._calculate_end_date(
                subscription.start_date,
                data['billing_cycle']
            )
            update_data['end_date'] = subscription.end_date
        
        # Add updated_at
        subscription.updated_at = datetime.utcnow()
        update_data['updated_at'] = subscription.updated_at
        
        # Update subscription in database
        result = self.subscriptions_collection.update_one(
            {'_id': oid},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            raise ValueError("Subscription not found")
        
        return self._format_subscription_response(subscription)
    
    def update_custom_settings(self, subscription_id: str, custom_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update only custom settings for a subscription."""
        oid = ObjectId(subscription_id)
        
        # Get current subscription
        subscription_doc = self.subscriptions_collection.find_one({'_id': oid})
        if not subscription_doc:
            raise ValueError("Subscription not found")
        
        # Create subscription model instance
        subscription = Subscription.from_dict(subscription_doc)
        
        # Update custom settings
        subscription.custom_settings = custom_settings
        subscription.updated_at = datetime.utcnow()
        
        # Update in database
        result = self.subscriptions_collection.update_one(
            {'_id': oid},
            {
                '$set': {
                    'custom_settings': subscription.custom_settings,
                    'updated_at': subscription.updated_at
                }
            }
        )
        
        if result.matched_count == 0:
            raise ValueError("Subscription not found")
        
        return self._format_subscription_response(subscription)
    
    def get_subscription_settings(self, subscription_id: str) -> Dict[str, Any]:
        """Get effective settings for a subscription (product defaults + custom settings)."""
        oid = ObjectId(subscription_id)
        
        # Get subscription
        subscription_doc = self.subscriptions_collection.find_one({'_id': oid})
        if not subscription_doc:
            raise ValueError("Subscription not found")
        
        subscription = Subscription.from_dict(subscription_doc)
        
        # Get product defaults if product exists
        product_defaults = {}
        if subscription.product_id:
            product = self.products_collection.find_one({'_id': subscription.product_id})
            if product and product.get('customizable', False):
                product_defaults = product.get('default_settings', {})
        
        # Get effective settings
        effective_settings = subscription.get_effective_settings(product_defaults)
        
        return {
            'subscription_id': subscription_id,
            'product_defaults': product_defaults,
            'custom_settings': subscription.custom_settings,
            'effective_settings': effective_settings
        }
    
    def apply_product_defaults_to_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Apply product default settings to subscription if missing."""
        oid = ObjectId(subscription_id)
        
        # Get subscription
        subscription_doc = self.subscriptions_collection.find_one({'_id': oid})
        if not subscription_doc:
            raise ValueError("Subscription not found")
        
        subscription = Subscription.from_dict(subscription_doc)
        
        # Get product defaults if product exists
        if not subscription.product_id:
            raise ValueError("Subscription has no associated product")
        
        product = self.products_collection.find_one({'_id': subscription.product_id})
        if not product:
            raise ValueError("Associated product not found")
        
        if not product.get('customizable', False):
            raise ValueError("Product is not customizable")
        
        # Apply defaults
        default_settings = product.get('default_settings', {})
        if default_settings:
            subscription.apply_product_defaults(default_settings)
            
            # Update in database
            self.subscriptions_collection.update_one(
                {'_id': oid},
                {
                    '$set': {
                        'custom_settings': subscription.custom_settings,
                        'updated_at': subscription.updated_at
                    }
                }
            )
        
        return self._format_subscription_response(subscription)
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription."""
        oid = ObjectId(subscription_id)
        
        # Get current subscription
        subscription_doc = self.subscriptions_collection.find_one({'_id': oid})
        if not subscription_doc:
            raise ValueError("Subscription not found")
        
        subscription = Subscription.from_dict(subscription_doc)
        
        if subscription.status in ['canceled', 'expired']:
            raise ValueError("Subscription is already canceled or expired")
        
        # Cancel subscription
        now = datetime.utcnow()
        subscription.status = 'canceled'
        subscription.canceled_at = now
        subscription.updated_at = now
        
        result = self.subscriptions_collection.update_one(
            {'_id': oid},
            {
                '$set': {
                    'status': subscription.status,
                    'canceled_at': subscription.canceled_at,
                    'updated_at': subscription.updated_at
                }
            }
        )
        
        if result.matched_count == 0:
            raise ValueError("Subscription not found")
        
        return self._format_subscription_response(subscription)
    
    def renew_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Renew a subscription."""
        oid = ObjectId(subscription_id)
        
        # Get current subscription
        subscription_doc = self.subscriptions_collection.find_one({'_id': oid})
        if not subscription_doc:
            raise ValueError("Subscription not found")
        
        subscription = Subscription.from_dict(subscription_doc)
        
        if subscription.status not in ['expired', 'canceled']:
            raise ValueError("Only expired or canceled subscriptions can be renewed")
        
        # Renew subscription
        now = datetime.utcnow()
        subscription.status = 'active'
        subscription.start_date = now
        subscription.end_date = self._calculate_end_date(now, subscription.billing_cycle)
        subscription.canceled_at = None
        subscription.updated_at = now
        
        result = self.subscriptions_collection.update_one(
            {'_id': oid},
            {
                '$set': {
                    'status': subscription.status,
                    'start_date': subscription.start_date,
                    'end_date': subscription.end_date,
                    'canceled_at': subscription.canceled_at,
                    'updated_at': subscription.updated_at
                }
            }
        )
        
        if result.matched_count == 0:
            raise ValueError("Subscription not found")
        
        return self._format_subscription_response(subscription)
    
    def get_customer_subscriptions(self, customer_id: str) -> list:
        """Get all subscriptions for a customer."""
        customer_oid = ObjectId(customer_id)
        
        # Check if customer exists
        customer = self.customers_collection.find_one({'_id': customer_oid})
        if not customer:
            raise ValueError("Customer not found")
        
        # Get subscriptions
        subscriptions_docs = list(self.subscriptions_collection.find({'customer_id': customer_oid}))
        
        # Convert to subscription models and format
        subscriptions = []
        for doc in subscriptions_docs:
            subscription = Subscription.from_dict(doc)
            subscriptions.append(self._format_subscription_response(subscription))
        
        return subscriptions
    
    def check_expired_subscriptions(self) -> int:
        """Check and update expired subscriptions."""
        now = datetime.utcnow()
        
        # Find active subscriptions that have expired
        expired_subscriptions = self.subscriptions_collection.find({
            'status': 'active',
            'end_date': {'$lt': now}
        })
        
        count = 0
        for subscription_doc in expired_subscriptions:
            # Update to expired status
            self.subscriptions_collection.update_one(
                {'_id': subscription_doc['_id']},
                {
                    '$set': {
                        'status': 'expired',
                        'updated_at': now
                    }
                }
            )
            count += 1
        
        return count
    
    def _calculate_end_date(self, start_date: datetime, billing_cycle: str) -> datetime:
        """Calculate end date based on billing cycle."""
        if billing_cycle == 'monthly':
            return start_date + timedelta(days=30)
        elif billing_cycle == 'yearly':
            return start_date + timedelta(days=365)
        elif billing_cycle == 'weekly':
            return start_date + timedelta(days=7)
        else:
            return start_date + timedelta(days=30)  # Default to monthly
    
    def _format_subscription_response(self, subscription: Subscription) -> Dict[str, Any]:
        """Format subscription for API response."""
        response = subscription.to_dict()
        
        # Convert ObjectIds to strings
        response['_id'] = str(subscription._id)
        response['customer_id'] = str(subscription.customer_id)
        if subscription.product_id:
            response['product_id'] = str(subscription.product_id)
        
        return response
    
    def subscribe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete subscription creation with advanced features.
        
        This method handles:
        - Product price/currency/billing_cycle inheritance if not specified
        - Automatic application of product defaults to custom_settings
        - Custom end date support (overrides billing cycle calculation)
        - Trial subscription management
        - Enhanced validation and error handling
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Subscribe method called with data: {data}")
        
        try:
            # Convert string IDs to ObjectIds
            customer_id = ObjectId(data['customer_id'])
            product_id = ObjectId(data['product_id'])
            logger.info(f"Converted IDs - customer_id: {customer_id}, product_id: {product_id}")
            
            # Validate customer exists
            customer = self.customers_collection.find_one({'_id': customer_id})
            if not customer:
                logger.error(f"Customer not found: {customer_id}")
                raise ValueError("Customer not found")
            logger.info(f"Customer found: {customer.get('name', 'Unknown')}")
            
            # Validate product exists and get product info
            product = self.products_collection.find_one({'_id': product_id})
            if not product:
                logger.error(f"Product not found: {product_id}")
                raise ValueError("Product not found")
            logger.info(f"Product found: {product.get('name', 'Unknown')}")
            
            if not product.get('is_active', True):
                logger.error(f"Product is not active: {product_id}")
                raise ValueError("Product is not active")
            
            # Inherit product properties if not explicitly provided
            amount = data.get('amount')
            if amount is None:
                amount = product.get('price', Decimal('0.00'))
                logger.info(f"Amount inherited from product: {amount}")
            if isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            logger.info(f"Final amount: {amount}")
            
            currency = data.get('currency') or product.get('currency', 'USD')
            billing_cycle = data.get('billing_cycle') or product.get('billing_cycle', 'monthly')
            logger.info(f"Currency: {currency}, Billing cycle: {billing_cycle}")
            
            # Determine subscription dates
            start_date = data.get('start_date')
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    logger.info(f"Start date converted from string: {start_date}")
            else:
                start_date = datetime.utcnow().replace(tzinfo=timezone.utc)
                logger.info(f"Start date set to now: {start_date}")
                
            trial_end_date = data.get('trial_end_date')
            if trial_end_date and isinstance(trial_end_date, str):
                trial_end_date = datetime.fromisoformat(trial_end_date.replace('Z', '+00:00'))
                logger.info(f"Trial end date converted from string: {trial_end_date}")
            
            # Handle trial period from product if trial_end_date not specified but product has trial
            if not trial_end_date and product.get('trial_period_days', 0) > 0:
                trial_end_date = start_date + timedelta(days=product['trial_period_days'])
                logger.info(f"Trial end date calculated from product: {trial_end_date}")
            
            # Determine subscription status - respect user input or calculate automatically
            status = data.get('status')
            if not status:
                # Auto-calculate status only if not explicitly provided
                status = 'trial' if trial_end_date and trial_end_date > datetime.utcnow().replace(tzinfo=timezone.utc) else 'active'
                logger.info(f"Status auto-calculated: {status}")
            else:
                logger.info(f"Status from user input: {status}")
            
            # Calculate end date - custom end_date overrides billing cycle calculation
            end_date = data.get('end_date')
            if end_date:
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    logger.info(f"End date converted from string: {end_date}")
            else:
                end_date = self._calculate_end_date(start_date, billing_cycle)
                logger.info(f"End date calculated: {end_date}")
                
        except Exception as e:
            logger.error(f"Error in subscribe data processing: {str(e)}", exc_info=True)
            raise
        
        # Create subscription data
        subscription_data = {
            'customer_id': customer_id,
            'product_id': product_id,
            'amount': amount,
            'currency': currency,
            'billing_cycle': billing_cycle,
            'status': status,
            'custom_settings': data.get('custom_settings', {}),
            'start_date': start_date,
            'end_date': end_date,
            'trial_end_date': trial_end_date,
            'metadata': data.get('metadata', {})
        }
        logger.info(f"Subscription data prepared: {subscription_data}")
        
        # Create subscription model instance
        try:
            subscription = Subscription.from_dict(subscription_data)
            logger.info(f"Subscription model instance created successfully")
        except Exception as e:
            logger.error(f"Error creating subscription model: {str(e)}", exc_info=True)
            raise
        
        # Apply product default settings if requested and product is customizable
        apply_defaults = data.get('apply_product_defaults', True)
        if apply_defaults and product.get('customizable', False):
            default_settings = product.get('default_settings', {})
            if default_settings:
                logger.info(f"Applying product defaults: {default_settings}")
                subscription.apply_product_defaults(default_settings)
                logger.info(f"Applied defaults. Custom settings now: {subscription.custom_settings}")
        
        # Add auto_renew metadata if specified
        if 'auto_renew' in data:
            subscription.metadata['auto_renew'] = data['auto_renew']
            logger.info(f"Added auto_renew metadata: {data['auto_renew']}")
        
        # Validate subscription business rules
        try:
            logger.info("Validating subscription business rules...")
            self._validate_subscription_business_rules(subscription, product)
            logger.info("Business rules validation passed")
        except Exception as e:
            logger.error(f"Business rules validation failed: {str(e)}")
            raise
        
        # Convert to dict for database insertion
        try:
            subscription_doc = subscription.to_dict()
            subscription_doc.pop('_id', None)  # Remove _id if present
            logger.info(f"Subscription document for DB: {subscription_doc}")
        except Exception as e:
            logger.error(f"Error converting subscription to dict: {str(e)}", exc_info=True)
            raise
        
        # Insert subscription
        try:
            logger.info("Inserting subscription into database...")
            result = self.subscriptions_collection.insert_one(subscription_doc)
            logger.info(f"Subscription inserted with ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Error inserting subscription: {str(e)}", exc_info=True)
            raise
        
        # Return created subscription with proper formatting
        try:
            subscription._id = result.inserted_id
            response = self._format_subscription_response(subscription)
            
            # Add product information to response for convenience
            response['product_info'] = {
                'name': product.get('name'),
                'description': product.get('description'),
                'features': product.get('features', []),
                'customizable': product.get('customizable', False)
            }
            
            logger.info(f"Subscribe method completed successfully. Response prepared.")
            return response
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}", exc_info=True)
            raise
    
    def _validate_subscription_business_rules(self, subscription: Subscription, product: Dict[str, Any]) -> None:
        """Validate business rules for subscription creation."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Validating business rules for subscription: customer_id={subscription.customer_id}, product_id={subscription.product_id}")
        
        # Check if customer already has active subscription for this product
        logger.info("Checking for existing active subscriptions...")
        existing_subscription = self.subscriptions_collection.find_one({
            'customer_id': subscription.customer_id,
            'product_id': subscription.product_id,
            'status': {'$in': ['active', 'trial']}
        })
        
        if existing_subscription:
            logger.error(f"Found existing active subscription: {existing_subscription['_id']}")
            raise ValueError("Customer already has an active subscription for this product")
        logger.info("No existing active subscriptions found")
        
        # Validate trial period
        if subscription.trial_end_date:
            logger.info(f"Validating trial period: start={subscription.start_date}, trial_end={subscription.trial_end_date}")
            
            # Ensure both dates are comparable (make both timezone-aware if needed)
            start_date = subscription.start_date
            trial_end_date = subscription.trial_end_date
            
            # If start_date is naive, make it UTC aware
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
                logger.info(f"Converted start_date to UTC: {start_date}")
            
            # If trial_end_date is naive, make it UTC aware
            if trial_end_date.tzinfo is None:
                trial_end_date = trial_end_date.replace(tzinfo=timezone.utc)
                logger.info(f"Converted trial_end_date to UTC: {trial_end_date}")
            
            if trial_end_date <= start_date:
                logger.error("Trial end date is before or equal to start date")
                raise ValueError("Trial end date must be after start date")
            logger.info("Trial period validation passed")
        
        # Validate end date
        logger.info(f"Validating end date: start={subscription.start_date}, end={subscription.end_date}")
        
        # Ensure both dates are comparable (make both timezone-aware if needed)
        start_date = subscription.start_date
        end_date = subscription.end_date
        
        # If start_date is naive, make it UTC aware
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        
        # If end_date is naive, make it UTC aware
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        
        if end_date <= start_date:
            logger.error("End date is before or equal to start date")
            raise ValueError("End date must be after start date")
        logger.info("End date validation passed")
        
        # Validate custom settings against product's customizable fields
        if subscription.custom_settings and product.get('customizable', False):
            logger.info(f"Validating custom settings: {subscription.custom_settings}")
            customizable_fields = product.get('customizable_fields', [])
            logger.info(f"Product customizable fields: {customizable_fields}")
            
            if customizable_fields:  # If specific fields are defined, validate against them
                invalid_fields = [
                    field for field in subscription.custom_settings.keys()
                    if field not in customizable_fields
                ]
                if invalid_fields:
                    logger.error(f"Invalid custom fields found: {invalid_fields}")
                    raise ValueError(f"Invalid custom fields: {', '.join(invalid_fields)}. "
                                   f"Allowed fields: {', '.join(customizable_fields)}")
                logger.info("Custom settings validation passed")
        else:
            logger.info("No custom settings to validate or product not customizable")
        
        logger.info("All business rules validation passed") 