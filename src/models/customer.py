"""Customer model and schema definitions."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from bson import ObjectId
from marshmallow import Schema, fields, validate, post_load, ValidationError


@dataclass
class Customer:
    """Customer data model."""
    
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _id: Optional[ObjectId] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'postal_code': self.postal_code,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self._id:
            data['_id'] = self._id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        """Create from dictionary."""
        return cls(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            status=data.get('status', 'active'),
            created_at=data.get('created_at', datetime.utcnow()),
            updated_at=data.get('updated_at', datetime.utcnow()),
            _id=data.get('_id')
        )
    
    def update(self, **kwargs) -> None:
        """Update customer attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


class CustomerSchema(Schema):
    """Customer validation schema."""
    
    _id = fields.String(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=120)
    )
    phone = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=20)
    )
    address = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=200)
    )
    city = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100)
    )
    country = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100)
    )
    postal_code = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=20)
    )
    status = fields.String(
        validate=validate.OneOf(["active", "inactive", "suspended"]),
        load_default="active"
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @post_load
    def make_customer(self, data: Dict[str, Any], **kwargs) -> Customer:
        """Create Customer instance from validated data."""
        return Customer(**data)
    
    def handle_error(self, error: ValidationError, data: Dict[str, Any], **kwargs):
        """Handle validation errors."""
        raise ValidationError(error.messages)


class CustomerUpdateSchema(Schema):
    """Customer update validation schema."""
    
    name = fields.String(
        validate=validate.Length(min=2, max=100),
        load_default=None
    )
    email = fields.Email(
        validate=validate.Length(max=120),
        load_default=None
    )
    phone = fields.String(
        validate=validate.Length(max=20),
        load_default=None,
        allow_none=True
    )
    address = fields.String(
        validate=validate.Length(max=200),
        load_default=None,
        allow_none=True
    )
    city = fields.String(
        validate=validate.Length(max=100),
        load_default=None,
        allow_none=True
    )
    country = fields.String(
        validate=validate.Length(max=100),
        load_default=None,
        allow_none=True
    )
    postal_code = fields.String(
        validate=validate.Length(max=20),
        load_default=None,
        allow_none=True
    )
    status = fields.String(
        validate=validate.OneOf(["active", "inactive", "suspended"]),
        load_default=None
    )


# Schema instances
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_update_schema = CustomerUpdateSchema() 