"""Product routes for REST API."""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from models.product import Product, product_schema, products_schema, product_update_schema
from repositories.mongo_client import MongoClient
from utils.validators import validate_object_id

products_bp = Blueprint('products', __name__)


@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering."""
    try:
        collection = current_app.mongo.get_collection('products')
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        is_active = request.args.get('is_active')
        billing_cycle = request.args.get('billing_cycle')
        customizable = request.args.get('customizable')
        search = request.args.get('search')
        
        # Build query
        query = {}
        if is_active is not None:
            query['is_active'] = is_active.lower() == 'true'
        if billing_cycle:
            query['billing_cycle'] = billing_cycle
        if customizable is not None:
            query['customizable'] = customizable.lower() == 'true'
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        # Execute query with pagination
        skip = (page - 1) * per_page
        cursor = collection.find(query).skip(skip).limit(per_page).sort('created_at', -1)
        
        # Get total count
        total = collection.count_documents(query)
        
        # Convert documents to product objects
        products = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            products.append(doc)
        
        return jsonify({
            'products': products,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting products: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product."""
    try:
        # Validate request data
        data = product_schema.load(request.get_json())
        
        # Create product document
        product_doc = data.to_dict()
        product_doc.pop('_id', None)  # Remove _id if present
        
        # Insert into database
        collection = current_app.mongo.get_collection('products')
        result = collection.insert_one(product_doc)
        
        # Return created product
        product_doc['_id'] = str(result.inserted_id)
        return jsonify(product_doc), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except DuplicateKeyError:
        return jsonify({'error': 'Product with this name already exists'}), 409
    except Exception as e:
        current_app.logger.error(f"Error creating product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    try:
        # Validate ObjectId
        if not validate_object_id(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        # Find product
        collection = current_app.mongo.get_collection('products')
        product = collection.find_one({'_id': ObjectId(product_id)})
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Convert ObjectId to string
        product['_id'] = str(product['_id'])
        
        return jsonify(product), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product."""
    try:
        # Validate ObjectId
        if not validate_object_id(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        # Validate request data
        data = product_update_schema.load(request.get_json())
        
        # Remove None values and convert Decimal to float for MongoDB
        update_data = {}
        for k, v in data.items():
            if v is not None:
                if k == 'price':
                    update_data[k] = float(v)  # Convert Decimal to float
                else:
                    update_data[k] = v
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Add updated_at
        from datetime import datetime
        update_data['updated_at'] = datetime.utcnow()
        
        # Update product
        collection = current_app.mongo.get_collection('products')
        result = collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        # Return updated product
        product = collection.find_one({'_id': ObjectId(product_id)})
        product['_id'] = str(product['_id'])
        
        return jsonify(product), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except DuplicateKeyError:
        return jsonify({'error': 'Product with this name already exists'}), 409
    except Exception as e:
        current_app.logger.error(f"Error updating product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product."""
    try:
        # Validate ObjectId
        if not validate_object_id(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        # Check if product has active subscriptions
        subscriptions_collection = current_app.mongo.get_collection('subscriptions')
        active_subscriptions = subscriptions_collection.count_documents({
            'product_id': ObjectId(product_id),
            'status': {'$in': ['active', 'trial']}
        })
        
        if active_subscriptions > 0:
            return jsonify({
                'error': 'Cannot delete product with active subscriptions'
            }), 400
        
        # Delete product
        collection = current_app.mongo.get_collection('products')
        result = collection.delete_one({'_id': ObjectId(product_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products/<product_id>/activate', methods=['POST'])
def activate_product(product_id):
    """Activate a product."""
    try:
        # Validate ObjectId
        if not validate_object_id(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        # Update product status
        collection = current_app.mongo.get_collection('products')
        from datetime import datetime
        
        result = collection.update_one(
            {'_id': ObjectId(product_id)},
            {
                '$set': {
                    'is_active': True,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        # Return updated product
        product = collection.find_one({'_id': ObjectId(product_id)})
        product['_id'] = str(product['_id'])
        
        return jsonify(product), 200
        
    except Exception as e:
        current_app.logger.error(f"Error activating product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products/<product_id>/deactivate', methods=['POST'])
def deactivate_product(product_id):
    """Deactivate a product."""
    try:
        # Validate ObjectId
        if not validate_object_id(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        # Update product status
        collection = current_app.mongo.get_collection('products')
        from datetime import datetime
        
        result = collection.update_one(
            {'_id': ObjectId(product_id)},
            {
                '$set': {
                    'is_active': False,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        # Return updated product
        product = collection.find_one({'_id': ObjectId(product_id)})
        product['_id'] = str(product['_id'])
        
        return jsonify(product), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deactivating product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 