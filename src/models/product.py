"""Product model and schema definitions."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from decimal import Decimal
from bson import ObjectId
from marshmallow import Schema, fields, validate, post_load, ValidationError


@dataclass
class Product:
    """Product data model."""
    
    name: str
    description: Optional[str] = None
    price: Decimal = Decimal('0.00')
    currency: str = "USD"
    billing_cycle: str = "monthly"  # monthly, yearly, weekly
    trial_period_days: int = 0
    features: List[str] = field(default_factory=list)
    is_active: bool = True
    customizable: bool = False
    customizable_fields: List[str] = field(default_factory=list)
    default_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _id: Optional[ObjectId] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'currency': self.currency,
            'billing_cycle': self.billing_cycle,
            'trial_period_days': self.trial_period_days,
            'features': self.features,
            'is_active': self.is_active,
            'customizable': self.customizable,
            'customizable_fields': self.customizable_fields,
            'default_settings': self.default_settings,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self._id:
            data['_id'] = self._id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Create from dictionary."""
        return cls(
            name=data.get('name'),
            description=data.get('description'),
            price=Decimal(str(data.get('price', '0.00'))),
            currency=data.get('currency', 'USD'),
            billing_cycle=data.get('billing_cycle', 'monthly'),
            trial_period_days=data.get('trial_period_days', 0),
            features=data.get('features', []),
            is_active=data.get('is_active', True),
            customizable=data.get('customizable', False),
            customizable_fields=data.get('customizable_fields', []),
            default_settings=data.get('default_settings', {}),
            created_at=data.get('created_at', datetime.utcnow()),
            updated_at=data.get('updated_at', datetime.utcnow()),
            _id=data.get('_id')
        )
    
    def update(self, **kwargs) -> None:
        """Update product attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'price':
                    setattr(self, key, Decimal(str(value)))
                else:
                    setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def get_monthly_price(self) -> Decimal:
        """Calculate monthly equivalent price."""
        if self.billing_cycle == 'monthly':
            return self.price
        elif self.billing_cycle == 'yearly':
            return self.price / 12
        elif self.billing_cycle == 'weekly':
            return self.price * 4
        else:
            return self.price


class ProductSchema(Schema):
    """Product validation schema."""
    
    _id = fields.String(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    description = fields.String(
        validate=validate.Length(max=500),
        allow_none=True
    )
    price = fields.Decimal(
        required=True,
        validate=validate.Range(min=0)
    )
    currency = fields.String(
        validate=validate.OneOf(['USD', 'EUR', 'GBP', 'JPY']),
        load_default='USD'
    )
    billing_cycle = fields.String(
        validate=validate.OneOf(['weekly', 'monthly', 'yearly']),
        load_default='monthly'
    )
    trial_period_days = fields.Integer(
        validate=validate.Range(min=0, max=365),
        allow_none=True
    )
    features = fields.List(
        fields.String(validate=validate.Length(max=100)),
        load_default=list
    )
    is_active = fields.Boolean(
        load_default=True
    )
    customizable = fields.Boolean(
        load_default=False
    )
    customizable_fields = fields.List(
        fields.String(validate=validate.Length(max=100)),
        load_default=list
    )
    default_settings = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        load_default=dict
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @post_load
    def make_product(self, data: Dict[str, Any], **kwargs) -> Product:
        """Create Product instance from validated data."""
        return Product(**data)
    
    def handle_error(self, error: ValidationError, data: Dict[str, Any], **kwargs):
        """Handle validation errors."""
        raise ValidationError(error.messages)


class ProductUpdateSchema(Schema):
    """Product update validation schema."""
    
    name = fields.String(
        validate=validate.Length(min=2, max=100),
        load_default=None
    )
    description = fields.String(
        validate=validate.Length(max=500),
        allow_none=True,
        load_default=None
    )
    price = fields.Decimal(
        validate=validate.Range(min=0),
        load_default=None
    )
    currency = fields.String(
        validate=validate.OneOf(['USD', 'EUR', 'GBP', 'JPY']),
        load_default=None
    )
    billing_cycle = fields.String(
        validate=validate.OneOf(['weekly', 'monthly', 'yearly']),
        load_default=None
    )
    trial_period_days = fields.Integer(
        validate=validate.Range(min=0, max=365),
        allow_none=True,
        load_default=None
    )
    features = fields.List(
        fields.String(validate=validate.Length(max=100)),
        load_default=None
    )
    is_active = fields.Boolean(load_default=None)
    customizable = fields.Boolean(load_default=None)
    customizable_fields = fields.List(
        fields.String(validate=validate.Length(max=100)),
        load_default=None
    )
    default_settings = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        load_default=None
    )


# Schema instances
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_update_schema = ProductUpdateSchema() 