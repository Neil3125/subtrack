"""AI-powered insights generation."""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.models import Category, Group, Customer, Subscription
from app.models.subscription import SubscriptionStatus
from app.ai.provider import AIProvider


class InsightsAnalyzer:
    """Analyzer for generating subscription insights."""
    
    def __init__(self, db: Session, ai_provider: AIProvider):
        self.db = db
        self.ai_provider = ai_provider
    
    async def generate_insights(
        self,
        category_id: Optional[int] = None,
        group_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        threshold_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive insights."""
        
        # Get deterministic data
        deterministic = self._get_deterministic_insights(
            category_id, group_id, customer_id, threshold_days
        )
        
        # Generate AI-powered insights if available
        ai_insights = None
        if self.ai_provider.is_available():
            ai_insights = await self._generate_ai_insights(deterministic)
        
        return {
            **deterministic,
            'ai_insights': ai_insights,
            'ai_enabled': self.ai_provider.is_available()
        }
    
    def _get_deterministic_insights(
        self,
        category_id: Optional[int],
        group_id: Optional[int],
        customer_id: Optional[int],
        threshold_days: int
    ) -> Dict[str, Any]:
        """Get deterministic insights from data."""
        
        # Build query based on scope
        query = self.db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        )
        
        if customer_id:
            query = query.filter(Subscription.customer_id == customer_id)
        elif group_id:
            query = query.join(Customer).filter(Customer.group_id == group_id)
        elif category_id:
            query = query.filter(Subscription.category_id == category_id)
        
        subscriptions = query.all()
        
        # Calculate metrics
        today = date.today()
        threshold_date = today + timedelta(days=threshold_days)
        
        expiring_soon = []
        overdue = []
        total_cost = 0.0
        vendor_costs = {}
        category_costs = {}
        
        for sub in subscriptions:
            # Cost calculations
            total_cost += sub.cost
            vendor_costs[sub.vendor_name] = vendor_costs.get(sub.vendor_name, 0) + sub.cost
            category_costs[sub.category_id] = category_costs.get(sub.category_id, 0) + sub.cost
            
            # Expiry checks
            if sub.next_renewal_date:
                if sub.next_renewal_date < today:
                    overdue.append({
                        'id': sub.id,
                        'vendor': sub.vendor_name,
                        'customer_id': sub.customer_id,
                        'cost': sub.cost,
                        'currency': sub.currency,
                        'days_overdue': (today - sub.next_renewal_date).days,
                        'next_renewal_date': sub.next_renewal_date.isoformat()
                    })
                elif sub.next_renewal_date <= threshold_date:
                    expiring_soon.append({
                        'id': sub.id,
                        'vendor': sub.vendor_name,
                        'customer_id': sub.customer_id,
                        'cost': sub.cost,
                        'currency': sub.currency,
                        'days_until_renewal': (sub.next_renewal_date - today).days,
                        'next_renewal_date': sub.next_renewal_date.isoformat()
                    })
        
        # Sort by urgency
        overdue.sort(key=lambda x: x['days_overdue'], reverse=True)
        expiring_soon.sort(key=lambda x: x['days_until_renewal'])
        
        # Top vendors by cost
        top_vendors = sorted(vendor_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_active_subscriptions': len(subscriptions),
            'total_monthly_cost': total_cost,  # Simplified - should normalize by cycle
            'expiring_soon': expiring_soon,
            'overdue': overdue,
            'top_vendors': [{'vendor': v, 'cost': c} for v, c in top_vendors],
            'category_breakdown': [
                {'category_id': cid, 'cost': cost} 
                for cid, cost in category_costs.items()
            ]
        }
    
    async def _generate_ai_insights(self, deterministic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations."""
        try:
            # Generate summary
            summary_prompt = f"""Based on this subscription data:
- Total active subscriptions: {deterministic_data['total_active_subscriptions']}
- Total monthly cost: ${deterministic_data['total_monthly_cost']:.2f}
- Expiring soon: {len(deterministic_data['expiring_soon'])}
- Overdue: {len(deterministic_data['overdue'])}
- Top vendors: {', '.join([v['vendor'] for v in deterministic_data['top_vendors'][:3]])}

Provide a brief summary (max 100 words) highlighting key insights and trends."""
            
            summary = await self.ai_provider.generate_completion(
                prompt=summary_prompt,
                system_prompt="You are a subscription management expert analyzing business spending patterns.",
                temperature=0.6,
                max_tokens=150
            )
            
            # Generate recommendations
            recommendations_prompt = f"""Based on this subscription data:
- {len(deterministic_data['overdue'])} overdue subscriptions
- {len(deterministic_data['expiring_soon'])} expiring within 30 days
- ${deterministic_data['total_monthly_cost']:.2f} total monthly cost

Provide 3-5 specific, actionable recommendations as a JSON array of strings."""
            
            recommendations_text = await self.ai_provider.generate_completion(
                prompt=recommendations_prompt,
                system_prompt="You are a subscription management expert. Provide recommendations as a valid JSON array.",
                temperature=0.7,
                max_tokens=300
            )
            
            # Try to parse JSON, fallback to plain text
            try:
                import json
                recommendations = json.loads(recommendations_text)
            except:
                # If not valid JSON, split by newlines
                recommendations = [r.strip() for r in recommendations_text.split('\n') if r.strip()]
            
            # Identify risk flags
            risk_flags = []
            if len(deterministic_data['overdue']) > 0:
                risk_flags.append({
                    'severity': 'high',
                    'message': f"{len(deterministic_data['overdue'])} overdue subscriptions require immediate attention"
                })
            if len(deterministic_data['expiring_soon']) > 10:
                risk_flags.append({
                    'severity': 'medium',
                    'message': f"High volume of upcoming renewals ({len(deterministic_data['expiring_soon'])}) in next 30 days"
                })
            if deterministic_data['total_monthly_cost'] > 10000:
                risk_flags.append({
                    'severity': 'low',
                    'message': f"High monthly spend (${deterministic_data['total_monthly_cost']:.2f}) - review for optimization"
                })
            
            return {
                'summary': summary,
                'recommendations': recommendations[:5],  # Limit to 5
                'risk_flags': risk_flags,
                'next_best_actions': self._generate_next_actions(deterministic_data)
            }
            
        except Exception as e:
            return {
                'summary': 'AI analysis unavailable',
                'recommendations': [],
                'risk_flags': [],
                'next_best_actions': self._generate_next_actions(deterministic_data),
                'error': str(e)
            }
    
    def _generate_next_actions(self, deterministic_data: Dict[str, Any]) -> List[str]:
        """Generate next best actions based on data."""
        actions = []
        
        if deterministic_data['overdue']:
            actions.append(f"Review and renew {len(deterministic_data['overdue'])} overdue subscriptions")
        
        if deterministic_data['expiring_soon']:
            top_expiring = deterministic_data['expiring_soon'][:3]
            for sub in top_expiring:
                actions.append(
                    f"Contact customer for {sub['vendor']} renewal (due in {sub['days_until_renewal']} days)"
                )
        
        if deterministic_data['total_active_subscriptions'] == 0:
            actions.append("Add your first subscription to start tracking")
        
        if not actions:
            actions.append("All subscriptions are up to date")
        
        return actions[:5]  # Limit to 5 actions
