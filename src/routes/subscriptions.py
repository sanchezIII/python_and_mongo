"""Subscription routes for REST API."""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from bson import ObjectId
from datetime import datetime, timedelta

from services.subscription_service import SubscriptionService
from services.analytics_service import AnalyticsService
from models.subscription import subscription_schema, subscription_update_schema, custom_settings_schema, subscribe_schema
from utils.validators import validate_object_id

subscriptions_bp = Blueprint('subscriptions', __name__)


@subscriptions_bp.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    """Get all subscriptions with optional filtering."""
    try:
        collection = current_app.mongo.get_collection('subscriptions')
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        status = request.args.get('status')
        customer_id = request.args.get('customer_id')
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        if customer_id:
            if not validate_object_id(customer_id):
                return jsonify({'error': 'Invalid customer ID'}), 400
            query['customer_id'] = ObjectId(customer_id)
        
        # Execute query with pagination
        skip = (page - 1) * per_page
        cursor = collection.find(query).skip(skip).limit(per_page).sort('created_at', -1)
        
        # Get total count
        total = collection.count_documents(query)
        
        # Convert documents
        subscriptions = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            doc['customer_id'] = str(doc['customer_id'])
            if 'product_id' in doc and doc['product_id']:
                doc['product_id'] = str(doc['product_id'])
            subscriptions.append(doc)
        
        return jsonify({
            'subscriptions': subscriptions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting subscriptions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """
    Complete subscription creation with advanced features (Subscribe).
    
    This endpoint provides:
    - Automatic inheritance of product properties (price, currency, billing_cycle)
    - Custom settings with product defaults application
    - Specific end date support (overrides billing cycle calculation)
    - Trial subscription management
    - Enhanced validation and business rules
    - Product information in response
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Subscribe endpoint called")
        
        # Get and log raw request data
        raw_data = request.get_json()
        logger.info(f"Raw request data: {raw_data}")
        
        # Validate request data using subscribe schema
        logger.info("Validating request data with schema...")
        data = subscribe_schema.load(raw_data)
        logger.info(f"Schema validation passed. Validated data: {data}")
        
        # Use subscription service to create subscription
        logger.info("Creating SubscriptionService instance...")
        service = SubscriptionService(current_app.mongo)
        
        logger.info("Calling service.subscribe() method...")
        subscription = service.subscribe(data)
        logger.info(f"Service call successful. Subscription created.")
        
        return jsonify(subscription), 201
        
    except ValidationError as e:
        logger.error(f"Schema validation error: {e.messages}")
        return jsonify({
            'error': 'Validation error',
            'details': e.messages,
            'hint': 'Check field requirements and formats'
        }), 400
    except ValueError as e:
        logger.error(f"ValueError in subscribe endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in subscribe endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    """Create a new subscription (Subscribe)."""
    try:
        # Validate request data using schema
        data = subscription_schema.load(request.get_json())
        
        # Convert subscription model back to dict for service
        subscription_data = {
            'customer_id': str(data.customer_id),
            'product_id': str(data.product_id) if data.product_id else None,
            'amount': data.amount,
            'currency': data.currency,
            'billing_cycle': data.billing_cycle,
            'status': data.status,
            'custom_settings': data.custom_settings,
            'start_date': data.start_date,
            'trial_end_date': data.trial_end_date,
            'metadata': data.metadata
        }
        
        # Use subscription service to create subscription
        service = SubscriptionService(current_app.mongo)
        subscription = service.create_subscription(subscription_data)
        
        return jsonify(subscription), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating subscription: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>', methods=['GET'])
def get_subscription(subscription_id):
    """Get a specific subscription by ID."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        collection = current_app.mongo.get_collection('subscriptions')
        subscription = collection.find_one({'_id': ObjectId(subscription_id)})
        
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404
        
        # Convert ObjectIds to strings
        subscription['_id'] = str(subscription['_id'])
        subscription['customer_id'] = str(subscription['customer_id'])
        if 'product_id' in subscription and subscription['product_id']:
            subscription['product_id'] = str(subscription['product_id'])
        
        return jsonify(subscription), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting subscription: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>', methods=['PUT'])
def update_subscription(subscription_id):
    """Update a subscription (EditSubscription)."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        # Validate request data
        data = subscription_update_schema.load(request.get_json())
        
        # Remove None values and convert Decimal to float
        update_data = {}
        for key, value in data.items():
            if value is not None:
                if key == 'amount':
                    update_data[key] = float(value)
                else:
                    update_data[key] = value
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Use subscription service to update subscription
        service = SubscriptionService(current_app.mongo)
        subscription = service.update_subscription(subscription_id, update_data)
        
        return jsonify(subscription), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating subscription: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>/settings', methods=['GET'])
def get_subscription_settings(subscription_id):
    """Get subscription settings (GetSettings)."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        service = SubscriptionService(current_app.mongo)
        settings = service.get_subscription_settings(subscription_id)
        
        return jsonify(settings), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting subscription settings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>/settings', methods=['PUT'])
def update_subscription_settings(subscription_id):
    """Update subscription custom settings (EditSubscription settings)."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        # Validate request data
        data = custom_settings_schema.load(request.get_json())
        
        service = SubscriptionService(current_app.mongo)
        subscription = service.update_custom_settings(subscription_id, data['custom_settings'])
        
        return jsonify(subscription), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating subscription settings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>/apply-defaults', methods=['POST'])
def apply_product_defaults(subscription_id):
    """Apply product default settings to subscription."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        service = SubscriptionService(current_app.mongo)
        subscription = service.apply_product_defaults_to_subscription(subscription_id)
        
        return jsonify(subscription), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error applying defaults: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>/status', methods=['GET'])
def get_subscription_status(subscription_id):
    """Get subscription status (GetSubscriptionStatus)."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        collection = current_app.mongo.get_collection('subscriptions')
        subscription = collection.find_one({'_id': ObjectId(subscription_id)})
        
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404
        
        # Determine if subscription is active or expired
        now = datetime.utcnow()
        is_active = subscription['status'] == 'active'
        is_expired = False
        
        if subscription.get('end_date') and subscription['end_date'] < now:
            is_expired = True
            is_active = False
        
        return jsonify({
            'subscription_id': subscription_id,
            'status': subscription['status'],
            'is_active': is_active,
            'is_expired': is_expired,
            'start_date': subscription.get('start_date'),
            'end_date': subscription.get('end_date'),
            'trial_end_date': subscription.get('trial_end_date'),
            'canceled_at': subscription.get('canceled_at')
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting subscription status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>/extend', methods=['POST'])
def extend_subscription(subscription_id):
    """Extend subscription with new expiration date (ExtendSubscription)."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        data = request.get_json()
        
        # Validate that we have either end_date or extension_period
        if 'end_date' not in data and 'extension_days' not in data:
            return jsonify({
                'error': 'Either end_date or extension_days is required'
            }), 400
        
        collection = current_app.mongo.get_collection('subscriptions')
        subscription = collection.find_one({'_id': ObjectId(subscription_id)})
        
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404
        
        # Calculate new end date
        if 'end_date' in data:
            try:
                new_end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
        else:
            extension_days = int(data['extension_days'])
            current_end_date = subscription.get('end_date', datetime.utcnow())
            new_end_date = current_end_date + timedelta(days=extension_days)
        
        # Update subscription
        result = collection.update_one(
            {'_id': ObjectId(subscription_id)},
            {
                '$set': {
                    'end_date': new_end_date,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Subscription not found'}), 404
        
        # Return updated subscription
        updated_subscription = collection.find_one({'_id': ObjectId(subscription_id)})
        updated_subscription['_id'] = str(updated_subscription['_id'])
        updated_subscription['customer_id'] = str(updated_subscription['customer_id'])
        if updated_subscription.get('product_id'):
            updated_subscription['product_id'] = str(updated_subscription['product_id'])
        
        return jsonify(updated_subscription), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error extending subscription: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    """Delete a subscription."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        collection = current_app.mongo.get_collection('subscriptions')
        result = collection.delete_one({'_id': ObjectId(subscription_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Subscription not found'}), 404
        
        return jsonify({'message': 'Subscription deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting subscription: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>/cancel', methods=['POST'])
def cancel_subscription(subscription_id):
    """Cancel a subscription."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        service = SubscriptionService(current_app.mongo)
        subscription = service.cancel_subscription(subscription_id)
        
        return jsonify(subscription), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error canceling subscription: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/<subscription_id>/renew', methods=['POST'])
def renew_subscription(subscription_id):
    """Renew a subscription."""
    try:
        if not validate_object_id(subscription_id):
            return jsonify({'error': 'Invalid subscription ID'}), 400
        
        service = SubscriptionService(current_app.mongo)
        subscription = service.renew_subscription(subscription_id)
        
        return jsonify(subscription), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error renewing subscription: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/subscriptions/stats', methods=['GET'])
def get_subscription_stats():
    """Get subscription statistics."""
    try:
        collection = current_app.mongo.get_collection('subscriptions')
        
        # Get status counts
        pipeline = [
            {'$group': {'_id': '$status', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        status_counts = list(collection.aggregate(pipeline))
        
        # Get total subscriptions
        total = collection.count_documents({})
        
        # Get active subscriptions
        active = collection.count_documents({'status': 'active'})
        
        # Get monthly revenue (simplified)
        revenue_pipeline = [
            {'$match': {'status': 'active'}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}},
        ]
        
        revenue_result = list(collection.aggregate(revenue_pipeline))
        monthly_revenue = revenue_result[0]['total'] if revenue_result else 0
        
        return jsonify({
            'total_subscriptions': total,
            'active_subscriptions': active,
            'monthly_revenue': monthly_revenue,
            'status_breakdown': status_counts
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting subscription stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions_bp.route('/analytics/financial-metrics', methods=['GET'])
def get_financial_metrics():
    """Get comprehensive financial metrics (MRR, ARR, ARPU, CLV, CRR, Churn, AOV, RPR)."""
    try:
        # Get period parameter (default 12 months)
        period_months = int(request.args.get('period_months', 12))
        
        # Validate period
        if period_months < 1 or period_months > 60:
            return jsonify({'error': 'period_months must be between 1 and 60'}), 400
        
        # Calculate metrics using analytics service
        analytics_service = AnalyticsService(current_app.mongo)
        metrics = analytics_service.get_financial_metrics(period_months)
        
        return jsonify(metrics), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error calculating financial metrics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 