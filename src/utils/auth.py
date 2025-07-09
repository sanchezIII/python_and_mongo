"""API Key authentication utilities."""

import os
from flask import request, jsonify

# API Keys válidas (en producción usar base de datos)
VALID_API_KEYS = set(os.getenv('API_KEYS', 'demo-key-123,prod-key-456').split(','))

def validate_api_key():
    """Validate API key from request headers."""
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in VALID_API_KEYS:
        return jsonify({'error': 'Invalid or missing API key'}), 401
    return None 