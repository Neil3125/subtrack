"""Comprehensive AI features for SubTrack."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models import Subscription, Customer, Category, Group
from app.ai.provider import get_ai_provider
import json


class AIFeatures:
    """Comprehensive AI-powered features for subscription management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_ai_provider()
    
    async def smart_categorization(self, subscription_name: str, plan_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Feature 1: Smart Subscription Categorization
        Automatically suggest the best category for a subscription based on its name and plan.
        """
        try:
            if not self.provider.is_available():
                return {"suggested_category": "Uncategorized", "confidence": 0, "reasoning": "AI provider not available"}
            
            categories = self.db.query(Category).all()
            category_list = [f"- {cat.name}: {cat.description}" for cat in categories]
            
            prompt = f"""Analyze this subscription and suggest the best category:

Subscription: {subscription_name}
Plan: {plan_name or 'Not specified'}

Available categories:
{chr(10).join(category_list)}

Respond with JSON only:
{{
    "suggested_category": "category name",
    "confidence": 0-100,
    "reasoning": "brief explanation"
}}"""
            
            response = await self.provider.generate_completion(prompt, max_tokens=200)
            return json.loads(response)
        except json.JSONDecodeError:
            return {"suggested_category": "Uncategorized", "confidence": 0, "reasoning": "Failed to parse AI response"}
        except Exception as e:
            return {"suggested_category": "Uncategorized", "confidence": 0, "reasoning": f"Error: {str(e)}"}
    
    async def cost_optimization(self, customer_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Feature 2: Cost Optimization Suggestions
        Analyze spending patterns and suggest ways to reduce costs.
        """
        try:
            query = self.db.query(Subscription).filter(Subscription.status == "active")
            if customer_id:
                query = query.filter(Subscription.customer_id == customer_id)
            
            subscriptions = query.all()
            
            # Prepare subscription data
            sub_data = []
            total_monthly = 0
            for sub in subscriptions:
                monthly_cost = self._normalize_to_monthly(sub.cost, sub.billing_cycle.value)
                total_monthly += monthly_cost
                sub_data.append({
                    "vendor": sub.vendor_name,
                    "plan": sub.plan_name,
                    "cost": sub.cost,
                    "cycle": sub.billing_cycle.value,
                    "monthly_equivalent": monthly_cost
                })
            
            if not self.provider.is_available():
                return {
                    "potential_savings": 0,
                    "suggestions": [],
                    "current_monthly_total": total_monthly,
                    "message": "AI provider not available"
                }
            
            prompt = f"""Analyze these subscriptions and provide cost optimization suggestions:

Total monthly cost: ${total_monthly:.2f}
Subscriptions:
{json.dumps(sub_data, indent=2)}

Respond with JSON only:
{{
    "potential_savings": 0.0,
    "suggestions": [
        {{
            "type": "duplicate|downgrade|bundle|cancel",
            "subscription": "vendor name",
            "action": "specific action to take",
            "estimated_savings": 0.0,
            "reasoning": "why this saves money"
        }}
    ],
    "priority": "high|medium|low"
}}"""
            
            response = await self.provider.generate_completion(prompt, max_tokens=800)
            result = json.loads(response)
            result["current_monthly_total"] = total_monthly
            return result
        except json.JSONDecodeError:
            return {
                "potential_savings": 0,
                "suggestions": [],
                "current_monthly_total": total_monthly if 'total_monthly' in locals() else 0,
                "error": "Failed to parse AI response"
            }
        except Exception as e:
            return {
                "potential_savings": 0,
                "suggestions": [],
                "current_monthly_total": total_monthly if 'total_monthly' in locals() else 0,
                "error": f"Error: {str(e)}"
            }
    
    async def smart_renewal_reminders(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Feature 3: Smart Renewal Reminders with Context
        Generate intelligent reminders with usage insights and recommendations.
        """
        try:
            cutoff_date = date.today() + timedelta(days=days_ahead)
            upcoming = self.db.query(Subscription).filter(
                Subscription.next_renewal_date <= cutoff_date,
                Subscription.next_renewal_date >= date.today(),
                Subscription.status == "active"
            ).all()
            
            reminders = []
            for sub in upcoming:
                days_until = (sub.next_renewal_date - date.today()).days
                
                # Create basic reminder
                basic_reminder = {
                    "subscription_id": sub.id,
                    "vendor": sub.vendor_name,
                    "days_until_renewal": days_until,
                    "urgency": "high" if days_until <= 7 else "medium" if days_until <= 14 else "low",
                    "message": f"{sub.vendor_name} renews in {days_until} days",
                    "action_items": ["Review usage", "Check if still needed"],
                    "considerations": ["Cost vs value", "Alternative options"],
                    "cost": sub.cost
                }
                
                # Try to enhance with AI if available
                if self.provider.is_available():
                    try:
                        prompt = f"""Generate a smart renewal reminder for this subscription:

Vendor: {sub.vendor_name}
Plan: {sub.plan_name or 'Standard'}
Cost: ${sub.cost} {sub.currency}
Renews in: {days_until} days
Billing: {sub.billing_cycle.value}

Respond with JSON only:
{{
    "urgency": "critical|high|medium|low",
    "message": "personalized reminder message",
    "action_items": ["specific actions to take before renewal"],
    "considerations": ["things to think about before renewing"]
}}"""
                        
                        response = await self.provider.generate_completion(prompt, max_tokens=300)
                        ai_reminder = json.loads(response)
                        # Merge AI data with basic data
                        basic_reminder.update(ai_reminder)
                    except:
                        pass  # Use basic reminder
                
                reminders.append(basic_reminder)
            
            return reminders
        except Exception as e:
            return []
    
    async def duplicate_detection(self) -> List[Dict[str, Any]]:
        """
        Feature 4: Duplicate Detection
        Find potential duplicate or overlapping subscriptions.
        """
        try:
            subscriptions = self.db.query(Subscription).filter(
                Subscription.status == "active"
            ).all()
            
            if not self.provider.is_available():
                return []
            
            sub_list = [
                f"{sub.id}: {sub.vendor_name} - {sub.plan_name or 'Standard'} (${sub.cost}/{sub.billing_cycle.value})"
                for sub in subscriptions
            ]
            
            prompt = f"""Analyze these subscriptions and identify potential duplicates or overlaps:

{chr(10).join(sub_list)}

Look for:
- Same vendor with multiple subscriptions
- Different vendors providing similar services
- Overlapping functionality

Respond with JSON only:
{{
    "duplicates": [
        {{
            "subscription_ids": [1, 2],
            "reason": "why these are duplicates",
            "recommendation": "what to do about it",
            "confidence": 0-100
        }}
    ]
}}"""
            
            response = await self.provider.generate_completion(prompt, max_tokens=600)
            return json.loads(response)["duplicates"]
        except Exception:
            return []
    
    async def usage_pattern_analysis(self, customer_id: int) -> Dict[str, Any]:
        """
        Feature 5: Usage Pattern Analysis
        Analyze subscription patterns and provide insights.
        """
        try:
            subscriptions = self.db.query(Subscription).filter(
                Subscription.customer_id == customer_id
            ).all()
            
            # Calculate statistics
            active_count = len([s for s in subscriptions if s.status.value == "active"])
            cancelled_count = len([s for s in subscriptions if s.status.value == "cancelled"])
            monthly_costs = [self._normalize_to_monthly(s.cost, s.billing_cycle.value) 
                            for s in subscriptions if s.status.value == "active"]
            total_monthly = sum(monthly_costs)
            
            base_result = {
                "spending_trend": "stable",
                "behavior_type": "moderate",
                "insights": [f"Customer has {active_count} active subscriptions"],
                "recommendations": ["Continue monitoring subscription usage"],
                "risk_factors": [],
                "total_monthly_cost": total_monthly,
                "active_count": active_count
            }
            
            if not self.provider.is_available():
                return base_result
            
            sub_summary = [
                f"{s.vendor_name} ({s.status.value}): ${s.cost}/{s.billing_cycle.value}"
                for s in subscriptions
            ]
            
            prompt = f"""Analyze this customer's subscription usage pattern:

Active subscriptions: {active_count}
Cancelled subscriptions: {cancelled_count}
Total monthly spend: ${total_monthly:.2f}

Subscriptions:
{chr(10).join(sub_summary)}

Respond with JSON only:
{{
    "spending_trend": "increasing|stable|decreasing",
    "behavior_type": "power_user|moderate|minimal",
    "insights": ["key insights about usage patterns"],
    "recommendations": ["personalized recommendations"],
    "risk_factors": ["potential issues to watch"]
}}"""
            
            response = await self.provider.generate_completion(prompt, max_tokens=500)
            result = json.loads(response)
            result["total_monthly_cost"] = total_monthly
            result["active_count"] = active_count
            return result
        except Exception:
            return base_result if 'base_result' in locals() else {
                "spending_trend": "unknown",
                "behavior_type": "moderate",
                "insights": [],
                "recommendations": [],
                "risk_factors": [],
                "total_monthly_cost": 0,
                "active_count": 0
            }
    
    async def budget_forecasting(self, months_ahead: int = 12) -> Dict[str, Any]:
        """
        Feature 6: Budget Forecasting
        Predict future subscription costs and budget needs.
        """
        try:
            active_subs = self.db.query(Subscription).filter(
                Subscription.status == "active"
            ).all()
            
            monthly_base = sum(
                self._normalize_to_monthly(s.cost, s.billing_cycle.value)
                for s in active_subs
            )
            
            # Simple linear forecast as fallback
            forecast = [{"month": i, "estimated_cost": monthly_base, "confidence": 50} 
                       for i in range(1, months_ahead + 1)]
            fallback_result = {
                "forecast": forecast,
                "total_forecasted": monthly_base * months_ahead,
                "current_monthly_baseline": monthly_base,
                "assumptions": ["Linear projection based on current costs"],
                "recommendations": ["Monitor for price changes", "Review annually"]
            }
            
            if not self.provider.is_available():
                return fallback_result
            
            sub_details = [
                {
                    "vendor": s.vendor_name,
                    "monthly_cost": self._normalize_to_monthly(s.cost, s.billing_cycle.value),
                    "billing_cycle": s.billing_cycle.value,
                    "next_renewal": str(s.next_renewal_date)
                }
                for s in active_subs
            ]
            
            prompt = f"""Forecast subscription costs for the next {months_ahead} months:

Current monthly baseline: ${monthly_base:.2f}
Active subscriptions: {len(active_subs)}

Subscription details:
{json.dumps(sub_details, indent=2)}

Consider:
- Typical price increases
- Seasonal patterns
- Growth trends

Respond with JSON only:
{{
    "forecast": [
        {{"month": 1, "estimated_cost": 0.0, "confidence": 0-100}}
    ],
    "total_forecasted": 0.0,
    "assumptions": ["key assumptions made"],
    "recommendations": ["budget recommendations"]
}}"""
            
            response = await self.provider.generate_completion(prompt, max_tokens=800)
            result = json.loads(response)
            result["current_monthly_baseline"] = monthly_base
            return result
        except Exception:
            return fallback_result if 'fallback_result' in locals() else {
                "forecast": [],
                "total_forecasted": 0,
                "current_monthly_baseline": 0,
                "assumptions": ["Error occurred"],
                "recommendations": []
            }
    
    async def smart_tagging(self, subscription_id: int) -> List[str]:
        """
        Feature 7: Smart Tagging and Metadata
        Generate intelligent tags and metadata for subscriptions.
        """
        try:
            sub = self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
            if not sub:
                return []
            
            # Fallback tags
            basic_tags = [sub.vendor_name.lower(), sub.billing_cycle.value, "subscription"]
            if sub.category:
                basic_tags.append(sub.category.name.lower())
            
            if not self.provider.is_available():
                return basic_tags
            
            prompt = f"""Generate smart tags for this subscription:

Vendor: {sub.vendor_name}
Plan: {sub.plan_name or 'Standard'}
Cost: ${sub.cost} {sub.currency}
Billing: {sub.billing_cycle.value}
Category: {sub.category.name if sub.category else 'Unknown'}
Notes: {sub.notes or 'None'}

Generate 5-8 relevant tags that would help with:
- Searching
- Categorization
- Cost management
- Feature identification

Respond with JSON only:
{{
    "tags": ["tag1", "tag2", "tag3"]
}}"""
            
            response = await self.provider.generate_completion(prompt, max_tokens=200)
            return json.loads(response)["tags"]
        except Exception:
            return basic_tags if 'basic_tags' in locals() else ["subscription"]
    
    async def natural_language_search(self, query: str) -> Dict[str, Any]:
        """
        Feature 8: Natural Language Search
        Search subscriptions using natural language queries.
        """
        try:
            all_subs = self.db.query(Subscription).all()
            
            if not self.provider.is_available():
                # Simple keyword search fallback
                query_lower = query.lower()
                matches = []
                for s in all_subs:
                    score = 0
                    if query_lower in s.vendor_name.lower():
                        score += 80
                    if s.plan_name and query_lower in s.plan_name.lower():
                        score += 60
                    if s.category and query_lower in s.category.name.lower():
                        score += 40
                    
                    if score > 0:
                        matches.append({
                            "subscription_id": s.id,
                            "vendor": s.vendor_name,
                            "cost": s.cost,
                            "relevance_score": min(score, 100),
                            "match_reason": "Keyword match"
                        })
                
                matches.sort(key=lambda x: x["relevance_score"], reverse=True)
                return {"matches": matches[:10], "query_interpretation": query}
            
            sub_list = [
                {
                    "id": s.id,
                    "vendor": s.vendor_name,
                    "plan": s.plan_name,
                    "cost": s.cost,
                    "cycle": s.billing_cycle.value,
                    "status": s.status.value,
                    "category": s.category.name if s.category else "Unknown"
                }
                for s in all_subs
            ]
            
            prompt = f"""User query: "{query}"

Find matching subscriptions from this list:
{json.dumps(sub_list, indent=2)}

Respond with JSON only:
{{
    "matches": [
        {{
            "subscription_id": 0,
            "relevance_score": 0-100,
            "match_reason": "why this matches the query"
        }}
    ],
    "query_interpretation": "how you understood the query"
}}"""
            
            response = await self.provider.generate_completion(prompt, max_tokens=600)
            result = json.loads(response)
            # Enhance with full subscription data
            for match in result["matches"]:
                sub = next((s for s in all_subs if s.id == match["subscription_id"]), None)
                if sub:
                    match["vendor"] = sub.vendor_name
                    match["cost"] = sub.cost
            return result
        except Exception:
            return {"matches": [], "query_interpretation": query}
    
    async def subscription_health_score(self, subscription_id: int) -> Dict[str, Any]:
        """
        Feature 10: Subscription Health Scoring
        Evaluate the health and value of a subscription.
        """
        try:
            sub = self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
            if not sub:
                return {"error": "Subscription not found"}
            
            days_until_renewal = (sub.next_renewal_date - date.today()).days
            monthly_cost = self._normalize_to_monthly(sub.cost, sub.billing_cycle.value)
            
            # Basic health score calculation
            base_score = 70
            if days_until_renewal < 0:
                base_score -= 30
            elif days_until_renewal < 7:
                base_score -= 10
            
            fallback_result = {
                "health_score": max(base_score, 0),
                "status": "excellent" if base_score >= 90 else "good" if base_score >= 70 else "fair" if base_score >= 50 else "poor",
                "factors": [{"aspect": "renewal", "score": base_score, "impact": "neutral"}],
                "recommendations": ["Review subscription value"],
                "warnings": ["Renews in {} days".format(days_until_renewal)] if days_until_renewal < 7 else []
            }
            
            if not self.provider.is_available():
                return fallback_result
            
            prompt = f"""Evaluate the health of this subscription:

Vendor: {sub.vendor_name}
Plan: {sub.plan_name or 'Standard'}
Cost: ${sub.cost} {sub.currency} per {sub.billing_cycle.value}
Monthly equivalent: ${monthly_cost:.2f}
Status: {sub.status.value}
Days until renewal: {days_until_renewal}
Notes: {sub.notes or 'None'}

Evaluate based on:
- Cost effectiveness
- Renewal status
- Usage indicators
- Value proposition

Respond with JSON only:
{{
    "health_score": 0-100,
    "status": "excellent|good|fair|poor|critical",
    "factors": [
        {{"aspect": "cost", "score": 0-100, "impact": "positive|negative|neutral"}}
    ],
    "recommendations": ["specific actions to improve health"],
    "warnings": ["potential issues"]
}}"""
            
            response = await self.provider.generate_completion(prompt, max_tokens=500)
            return json.loads(response)
        except Exception:
            return fallback_result if 'fallback_result' in locals() else {
                "health_score": 70,
                "status": "good",
                "factors": [],
                "recommendations": [],
                "warnings": []
            }
    
    def _normalize_to_monthly(self, cost: float, cycle: str) -> float:
        """Convert any billing cycle to monthly cost."""
        multipliers = {
            "weekly": 4.33,
            "monthly": 1,
            "quarterly": 1/3,
            "biannual": 1/6,
            "yearly": 1/12
        }
        return cost * multipliers.get(cycle, 1)
