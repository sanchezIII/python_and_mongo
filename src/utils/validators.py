"""Utility functions for validation and common operations."""

import re
from typing import Any, Dict, Optional
from bson import ObjectId
from bson.errors import InvalidId


def validate_object_id(oid: str) -> bool:
    """Validate if string is a valid MongoDB ObjectId."""
    try:
        ObjectId(oid)
        return True
    except (InvalidId, TypeError):
        return False


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it has between 7 and 15 digits
    return 7 <= len(digits) <= 15


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"


def validate_currency(currency: str) -> bool:
    """Validate currency code."""
    if not currency or not isinstance(currency, str):
        return False
    
    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY']
    return currency.upper() in valid_currencies


def validate_billing_cycle(cycle: str) -> bool:
    """Validate billing cycle."""
    if not cycle or not isinstance(cycle, str):
        return False
    
    valid_cycles = ['weekly', 'monthly', 'yearly']
    return cycle.lower() in valid_cycles


def validate_status(status: str, valid_statuses: list) -> bool:
    """Validate status against allowed values."""
    if not status or not isinstance(status, str):
        return False
    
    return status.lower() in [s.lower() for s in valid_statuses]


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input."""
    if not value or not isinstance(value, str):
        return ""
    
    # Strip whitespace
    value = value.strip()
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def parse_pagination_params(page: Any, per_page: Any) -> tuple[int, int]:
    """Parse and validate pagination parameters."""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 10
    except (ValueError, TypeError):
        page = 1
        per_page = 10
    
    # Ensure positive values
    page = max(1, page)
    per_page = max(1, min(100, per_page))  # Limit to 100 items per page
    
    return page, per_page


def build_search_query(search_term: str, fields: list) -> Dict[str, Any]:
    """Build MongoDB search query for multiple fields."""
    if not search_term or not fields:
        return {}
    
    search_term = sanitize_string(search_term)
    if not search_term:
        return {}
    
    # Create regex pattern for case-insensitive search
    pattern = {'$regex': search_term, '$options': 'i'}
    
    # Build $or query for multiple fields
    or_conditions = []
    for field in fields:
        or_conditions.append({field: pattern})
    
    return {'$or': or_conditions}


def validate_price(price: Any) -> tuple[bool, str]:
    """Validate price value."""
    if price is None:
        return False, "Price is required"
    
    try:
        price_float = float(price)
        if price_float < 0:
            return False, "Price cannot be negative"
        if price_float > 999999.99:
            return False, "Price is too large"
        return True, "Price is valid"
    except (ValueError, TypeError):
        return False, "Price must be a valid number"


def validate_date_range(start_date: Any, end_date: Any) -> tuple[bool, str]:
    """Validate date range."""
    from datetime import datetime
    
    if not start_date or not end_date:
        return False, "Both start and end dates are required"
    
    try:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start_date >= end_date:
            return False, "Start date must be before end date"
        
        return True, "Date range is valid"
    except (ValueError, TypeError) as e:
        return False, f"Invalid date format: {str(e)}"


def format_error_response(error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Format error response consistently."""
    response = {'error': error}
    if details:
        response['details'] = details
    return response


def format_success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """Format success response consistently."""
    response = {'data': data}
    if message:
        response['message'] = message
    return response


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def convert_objectid_to_string(data: Any) -> Any:
    """Recursively convert ObjectId to string in data structure."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid_to_string(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_string(item) for item in data]
    else:
        return data 