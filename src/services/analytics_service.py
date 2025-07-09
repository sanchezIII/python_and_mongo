"""Analytics service for financial metrics calculation."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict

from repositories.mongo_client import MongoClient


class AnalyticsService:
    """Service for calculating financial metrics."""
    
    def __init__(self, mongo_client: MongoClient):
        """Initialize analytics service."""
        self.mongo = mongo_client
        self.subscriptions_collection = mongo_client.get_collection('subscriptions')
        self.customers_collection = mongo_client.get_collection('customers')
    
    def get_financial_metrics(self, period_months: int = 12) -> Dict[str, Any]:
        """Calculate all financial metrics."""
        # Get all active subscriptions
        active_subscriptions = list(self.subscriptions_collection.find({'status': 'active'}))
        
        # Get all subscriptions for historical analysis
        all_subscriptions = list(self.subscriptions_collection.find())
        
        # Get all customers
        all_customers = list(self.customers_collection.find())
        
        # Calculate metrics
        mrr = self._calculate_mrr(active_subscriptions)
        arr = self._calculate_arr(mrr)
        arpu = self._calculate_arpu(active_subscriptions)
        clv = self._calculate_clv(all_subscriptions)
        crr = self._calculate_crr(all_subscriptions, period_months)
        churn_rate = self._calculate_churn_rate(all_subscriptions, period_months)
        aov = self._calculate_aov(all_subscriptions)
        rpr = self._calculate_rpr(all_subscriptions)
        
        return {
            'period_months': period_months,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'mrr': {
                    'value': round(mrr, 2),
                    'description': 'Monthly Recurring Revenue',
                    'unit': 'USD'
                },
                'arr': {
                    'value': round(arr, 2),
                    'description': 'Annual Recurring Revenue',
                    'unit': 'USD'
                },
                'arpu': {
                    'value': round(arpu, 2),
                    'description': 'Average Revenue Per User',
                    'unit': 'USD'
                },
                'clv': {
                    'value': round(clv, 2),
                    'description': 'Customer Lifetime Value',
                    'unit': 'USD'
                },
                'crr': {
                    'value': round(crr, 4),
                    'description': 'Customer Retention Rate',
                    'unit': 'percentage'
                },
                'churn_rate': {
                    'value': round(churn_rate, 4),
                    'description': 'Churn Rate',
                    'unit': 'percentage'
                },
                'aov': {
                    'value': round(aov, 2),
                    'description': 'Average Order Value',
                    'unit': 'USD'
                },
                'rpr': {
                    'value': round(rpr, 4),
                    'description': 'Repeat Purchase Rate',
                    'unit': 'percentage'
                }
            },
            'summary': {
                'total_active_subscriptions': len(active_subscriptions),
                'total_subscriptions': len(all_subscriptions),
                'total_customers': len(all_customers),
                'active_customers': len(set(sub['customer_id'] for sub in active_subscriptions))
            }
        }
    
    def _calculate_mrr(self, active_subscriptions: list) -> float:
        """Calculate Monthly Recurring Revenue."""
        total_mrr = 0
        
        for sub in active_subscriptions:
            amount = float(sub.get('amount', 0))
            billing_cycle = sub.get('billing_cycle', 'monthly')
            
            # Normalize to monthly
            if billing_cycle == 'monthly':
                monthly_amount = amount
            elif billing_cycle == 'yearly':
                monthly_amount = amount / 12
            elif billing_cycle == 'weekly':
                monthly_amount = amount * 4.33  # ~4.33 weeks per month
            else:
                monthly_amount = amount  # Default to monthly
            
            total_mrr += monthly_amount
        
        return total_mrr
    
    def _calculate_arr(self, mrr: float) -> float:
        """Calculate Annual Recurring Revenue."""
        return mrr * 12
    
    def _calculate_arpu(self, active_subscriptions: list) -> float:
        """Calculate Average Revenue Per User."""
        if not active_subscriptions:
            return 0
        
        total_revenue = sum(float(sub.get('amount', 0)) for sub in active_subscriptions)
        unique_customers = len(set(sub['customer_id'] for sub in active_subscriptions))
        
        return total_revenue / unique_customers if unique_customers > 0 else 0
    
    def _calculate_clv(self, all_subscriptions: list) -> float:
        """Calculate Customer Lifetime Value."""
        if not all_subscriptions:
            return 0
        
        # Group by customer
        customer_data = defaultdict(list)
        for sub in all_subscriptions:
            customer_data[sub['customer_id']].append(sub)
        
        total_clv = 0
        customer_count = 0
        
        for customer_id, subscriptions in customer_data.items():
            # Average purchase value for this customer
            avg_purchase = sum(float(sub.get('amount', 0)) for sub in subscriptions) / len(subscriptions)
            
            # Purchase frequency (subscriptions per customer)
            purchase_frequency = len(subscriptions)
            
            # Customer lifespan (from first to last subscription)
            if len(subscriptions) > 1:
                dates = [sub.get('created_at', datetime.utcnow()) for sub in subscriptions]
                dates = [d for d in dates if d is not None]
                if dates:
                    lifespan_days = (max(dates) - min(dates)).days
                    lifespan_months = max(lifespan_days / 30, 1)  # At least 1 month
                else:
                    lifespan_months = 1
            else:
                lifespan_months = 1
            
            customer_clv = avg_purchase * purchase_frequency * (lifespan_months / 12)
            total_clv += customer_clv
            customer_count += 1
        
        return total_clv / customer_count if customer_count > 0 else 0
    
    def _calculate_crr(self, all_subscriptions: list, period_months: int) -> float:
        """Calculate Customer Retention Rate."""
        now = datetime.utcnow()
        period_start = now - timedelta(days=period_months * 30)
        
        # Customers at the beginning of period
        customers_beginning = set()
        for sub in all_subscriptions:
            created_at = sub.get('created_at', now)
            if created_at <= period_start:
                customers_beginning.add(sub['customer_id'])
        
        # Customers at the end of period (still active)
        customers_end = set()
        for sub in all_subscriptions:
            if sub.get('status') == 'active':
                customers_end.add(sub['customer_id'])
        
        # New customers during period
        new_customers = set()
        for sub in all_subscriptions:
            created_at = sub.get('created_at', now)
            if created_at > period_start:
                new_customers.add(sub['customer_id'])
        
        if len(customers_beginning) == 0:
            return 0
        
        retained_customers = len(customers_end - new_customers)
        return retained_customers / len(customers_beginning)
    
    def _calculate_churn_rate(self, all_subscriptions: list, period_months: int) -> float:
        """Calculate Churn Rate."""
        now = datetime.utcnow()
        period_start = now - timedelta(days=period_months * 30)
        
        # Customers at the beginning of period
        customers_beginning = set()
        for sub in all_subscriptions:
            created_at = sub.get('created_at', now)
            if created_at <= period_start:
                customers_beginning.add(sub['customer_id'])
        
        # Lost customers during period
        lost_customers = set()
        for sub in all_subscriptions:
            canceled_at = sub.get('canceled_at')
            if canceled_at and canceled_at >= period_start:
                lost_customers.add(sub['customer_id'])
        
        if len(customers_beginning) == 0:
            return 0
        
        return len(lost_customers) / len(customers_beginning)
    
    def _calculate_aov(self, all_subscriptions: list) -> float:
        """Calculate Average Order Value."""
        if not all_subscriptions:
            return 0
        
        total_revenue = sum(float(sub.get('amount', 0)) for sub in all_subscriptions)
        total_orders = len(all_subscriptions)
        
        return total_revenue / total_orders
    
    def _calculate_rpr(self, all_subscriptions: list) -> float:
        """Calculate Repeat Purchase Rate."""
        if not all_subscriptions:
            return 0
        
        # Group by customer
        customer_subscription_count = defaultdict(int)
        for sub in all_subscriptions:
            customer_subscription_count[sub['customer_id']] += 1
        
        # Count customers with multiple subscriptions
        customers_with_multiple = sum(1 for count in customer_subscription_count.values() if count > 1)
        total_customers = len(customer_subscription_count)
        
        return customers_with_multiple / total_customers if total_customers > 0 else 0 