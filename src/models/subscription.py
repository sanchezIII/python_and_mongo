"""Subscription model and schema definitions."""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from decimal import Decimal
from bson import ObjectId
from marshmallow import Schema, fields, validate, post_load, ValidationError


@dataclass
class Subscription:
    """Subscription data model."""
    
    customer_id: ObjectId
    amount: Decimal
    status: str = "active"  # active, canceled, expired, trial
    currency: str = "USD"
    billing_cycle: str = "monthly"  # weekly, monthly, yearly
    product_id: Optional[ObjectId] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _id: Optional[ObjectId] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'customer_id': self.customer_id,
            'amount': float(self.amount),
            'status': self.status,
            'currency': self.currency,
            'billing_cycle': self.billing_cycle,
            'product_id': self.product_id,
            'custom_settings': self.custom_settings,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'trial_end_date': self.trial_end_date,
            'canceled_at': self.canceled_at,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self._id:
            data['_id'] = self._id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """Create from dictionary."""
        return cls(
            customer_id=data.get('customer_id'),
            amount=Decimal(str(data.get('amount', '0.00'))),
            status=data.get('status', 'active'),
            currency=data.get('currency', 'USD'),
            billing_cycle=data.get('billing_cycle', 'monthly'),
            product_id=data.get('product_id'),
            custom_settings=data.get('custom_settings', {}),
            start_date=data.get('start_date', datetime.utcnow()),
            end_date=data.get('end_date'),
            trial_end_date=data.get('trial_end_date'),
            canceled_at=data.get('canceled_at'),
            metadata=data.get('metadata', {}),
            created_at=data.get('created_at', datetime.utcnow()),
            updated_at=data.get('updated_at', datetime.utcnow()),
            _id=data.get('_id')
        )
    
    def update(self, **kwargs) -> None:
        """Update subscription attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'amount':
                    setattr(self, key, Decimal(str(value)))
                else:
                    setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def apply_product_defaults(self, product_settings: Dict[str, Any]) -> None:
        """Apply product default settings to subscription custom_settings."""
        if not self.custom_settings:
            self.custom_settings = {}
        
        # Only apply defaults for keys that don't exist in custom_settings
        for key, default_value in product_settings.items():
            if key not in self.custom_settings:
                self.custom_settings[key] = default_value
        
        self.updated_at = datetime.utcnow()
    
    def get_effective_settings(self, product_defaults: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get effective settings combining product defaults and custom settings."""
        effective_settings = {}
        
        # Start with product defaults if provided
        if product_defaults:
            effective_settings.update(product_defaults)
        
        # Override with custom settings
        effective_settings.update(self.custom_settings)
        
        return effective_settings
    
    def update_custom_setting(self, key: str, value: Any) -> None:
        """Update a specific custom setting."""
        if not self.custom_settings:
            self.custom_settings = {}
        
        self.custom_settings[key] = value
        self.updated_at = datetime.utcnow()
    
    def remove_custom_setting(self, key: str) -> None:
        """Remove a specific custom setting."""
        if self.custom_settings and key in self.custom_settings:
            del self.custom_settings[key]
            self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        now = datetime.utcnow()
        
        if self.status != 'active':
            return False
        
        if self.end_date and self.end_date < now:
            return False
        
        return True
    
    def is_in_trial(self) -> bool:
        """Check if subscription is in trial period."""
        if self.status != 'trial':
            return False
        
        if not self.trial_end_date:
            return False
        
        return datetime.utcnow() < self.trial_end_date


class SubscriptionSchema(Schema):
    """Subscription validation schema."""
    
    _id = fields.String(dump_only=True)
    customer_id = fields.String(
        required=True,
        validate=validate.Length(equal=24),  # ObjectId length
        error_messages={'required': 'Customer ID is required'}
    )
    product_id = fields.String(
        validate=validate.Length(equal=24),  # ObjectId length
        allow_none=True
    )
    amount = fields.Decimal(
        required=True,
        validate=validate.Range(min=0),
        error_messages={'required': 'Amount is required'}
    )
    currency = fields.String(
        validate=validate.OneOf(['USD', 'EUR', 'GBP', 'JPY']),
        missing='USD'
    )
    billing_cycle = fields.String(
        validate=validate.OneOf(['weekly', 'monthly', 'yearly']),
        missing='monthly'
    )
    status = fields.String(
        validate=validate.OneOf(['active', 'canceled', 'expired', 'trial']),
        missing='active'
    )
    custom_settings = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),  # Allow any value type
        missing=dict
    )
    start_date = fields.DateTime(missing=datetime.utcnow)
    end_date = fields.DateTime(allow_none=True)
    trial_end_date = fields.DateTime(allow_none=True)
    canceled_at = fields.DateTime(dump_only=True)
    metadata = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        missing=dict
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @post_load
    def make_subscription(self, data: Dict[str, Any], **kwargs) -> Subscription:
        """Create Subscription instance from validated data."""
        # Convert string IDs to ObjectIds
        if 'customer_id' in data:
            data['customer_id'] = ObjectId(data['customer_id'])
        if 'product_id' in data and data['product_id']:
            data['product_id'] = ObjectId(data['product_id'])
        
        return Subscription(**data)
    
    def handle_error(self, error: ValidationError, data: Dict[str, Any], **kwargs):
        """Handle validation errors."""
        raise ValidationError(error.messages)


class SubscriptionUpdateSchema(Schema):
    """Subscription update validation schema."""
    
    amount = fields.Decimal(
        validate=validate.Range(min=0),
        missing=None
    )
    currency = fields.String(
        validate=validate.OneOf(['USD', 'EUR', 'GBP', 'JPY']),
        missing=None
    )
    billing_cycle = fields.String(
        validate=validate.OneOf(['weekly', 'monthly', 'yearly']),
        missing=None
    )
    status = fields.String(
        validate=validate.OneOf(['active', 'canceled', 'expired', 'trial']),
        missing=None
    )
    custom_settings = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        missing=None
    )
    end_date = fields.DateTime(missing=None)
    trial_end_date = fields.DateTime(missing=None)
    metadata = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        missing=None
    )


class CustomSettingsUpdateSchema(Schema):
    """Schema for updating only custom settings."""
    
    custom_settings = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        required=True,
        error_messages={'required': 'Custom settings are required'}
    )


# Schema instances
subscription_schema = SubscriptionSchema()
subscriptions_schema = SubscriptionSchema(many=True)
subscription_update_schema = SubscriptionUpdateSchema()
custom_settings_schema = CustomSettingsUpdateSchema()

class SubscribeSchema(Schema):
    """Schema specifically for the Subscribe endpoint with full functionality."""
    
    customer_id = fields.String(
        required=True,
        validate=validate.Length(equal=24),  # ObjectId length
        error_messages={'required': 'Customer ID is required'}
    )
    product_id = fields.String(
        required=True,
        validate=validate.Length(equal=24),  # ObjectId length
        error_messages={'required': 'Product ID is required'}
    )
    amount = fields.Decimal(
        validate=validate.Range(min=0),
        missing=None  # If not provided, will use product price
    )
    currency = fields.String(
        validate=validate.OneOf(['USD', 'EUR', 'GBP', 'JPY']),
        missing=None  # If not provided, will use product currency
    )
    billing_cycle = fields.String(
        validate=validate.OneOf(['weekly', 'monthly', 'yearly']),
        missing=None  # If not provided, will use product billing_cycle
    )
    status = fields.String(
        validate=validate.OneOf(['active', 'canceled', 'expired', 'trial']),
        missing='active',
        description="Subscription status"
    )
    custom_settings = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        missing=dict,
        description="Custom settings for subscription customization"
    )
    apply_product_defaults = fields.Boolean(
        missing=True,
        description="Whether to apply product default settings automatically"
    )
    start_date = fields.DateTime(
        missing=None,  # If not provided, will use current datetime
        description="Subscription start date"
    )
    end_date = fields.DateTime(
        allow_none=True,
        description="Specific end date for subscription (overrides billing cycle calculation)"
    )
    trial_end_date = fields.DateTime(
        allow_none=True,
        description="Trial end date if subscription starts in trial"
    )
    auto_renew = fields.Boolean(
        missing=True,
        description="Whether subscription should auto-renew"
    )
    metadata = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        missing=dict,
        description="Additional metadata for the subscription"
    )
    
    @post_load
    def make_subscribe_data(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process and validate subscribe data."""
        # Convert string IDs to ObjectIds for internal processing
        if 'customer_id' in data:
            data['customer_id'] = ObjectId(data['customer_id'])
        if 'product_id' in data:
            data['product_id'] = ObjectId(data['product_id'])
        
        return data
    
    def handle_error(self, error: ValidationError, data: Dict[str, Any], **kwargs):
        """Handle validation errors."""
        raise ValidationError(error.messages)


# Add to schema instances
subscribe_schema = SubscribeSchema() 