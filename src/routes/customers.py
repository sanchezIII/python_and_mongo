"""Customer routes for REST API."""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from models.customer import Customer, customer_schema, customers_schema, customer_update_schema
from repositories.mongo_client import MongoClient
from utils.validators import validate_object_id

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers with optional filtering."""
    try:
        collection = current_app.mongo.get_collection('customers')
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        status = request.args.get('status')
        search = request.args.get('search')
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}}
            ]
        
        # Execute query with pagination
        skip = (page - 1) * per_page
        cursor = collection.find(query).skip(skip).limit(per_page).sort('created_at', -1)
        
        # Get total count
        total = collection.count_documents(query)
        
        # Convert documents to customer objects
        customers = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            customers.append(doc)
        
        return jsonify({
            'customers': customers,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting customers: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@customers_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create a new customer."""
    try:
        # Validate request data
        data = customer_schema.load(request.get_json())
        
        # Create customer document
        customer_doc = data.to_dict()
        customer_doc.pop('_id', None)  # Remove _id if present
        
        # Insert into database
        collection = current_app.mongo.get_collection('customers')
        result = collection.insert_one(customer_doc)
        
        # Return created customer
        customer_doc['_id'] = str(result.inserted_id)
        return jsonify(customer_doc), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except DuplicateKeyError:
        return jsonify({'error': 'Customer with this email already exists'}), 409
    except Exception as e:
        current_app.logger.error(f"Error creating customer: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@customers_bp.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a specific customer by ID."""
    try:
        # Validate ObjectId
        if not validate_object_id(customer_id):
            return jsonify({'error': 'Invalid customer ID'}), 400
        
        # Find customer
        collection = current_app.mongo.get_collection('customers')
        customer = collection.find_one({'_id': ObjectId(customer_id)})
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Convert ObjectId to string
        customer['_id'] = str(customer['_id'])
        
        return jsonify(customer), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting customer: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@customers_bp.route('/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update a customer."""
    try:
        # Validate ObjectId
        if not validate_object_id(customer_id):
            return jsonify({'error': 'Invalid customer ID'}), 400
        
        # Validate request data
        data = customer_update_schema.load(request.get_json())
        
        # Remove None values
        update_data = {k: v for k, v in data.items() if v is not None}
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Add updated_at
        from datetime import datetime
        update_data['updated_at'] = datetime.utcnow()
        
        # Update customer
        collection = current_app.mongo.get_collection('customers')
        result = collection.update_one(
            {'_id': ObjectId(customer_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Return updated customer
        customer = collection.find_one({'_id': ObjectId(customer_id)})
        customer['_id'] = str(customer['_id'])
        
        return jsonify(customer), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except DuplicateKeyError:
        return jsonify({'error': 'Customer with this email already exists'}), 409
    except Exception as e:
        current_app.logger.error(f"Error updating customer: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@customers_bp.route('/customers/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete a customer."""
    try:
        # Validate ObjectId
        if not validate_object_id(customer_id):
            return jsonify({'error': 'Invalid customer ID'}), 400
        
        # Check if customer has active subscriptions
        subscriptions_collection = current_app.mongo.get_collection('subscriptions')
        active_subscriptions = subscriptions_collection.count_documents({
            'customer_id': ObjectId(customer_id),
            'status': {'$in': ['active', 'trial']}
        })
        
        if active_subscriptions > 0:
            return jsonify({
                'error': 'Cannot delete customer with active subscriptions'
            }), 400
        
        # Delete customer
        collection = current_app.mongo.get_collection('customers')
        result = collection.delete_one({'_id': ObjectId(customer_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify({'message': 'Customer deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting customer: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 