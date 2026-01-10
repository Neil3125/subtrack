"""
Smart AI Features for SubTrack.

This module provides 4 AI-powered features:
1. Smart Link Intelligence - Extract subscription details from URLs
2. Budget Surgeon - Identify duplicate/redundant spending
3. Renewal Forecaster - Predict upcoming bill totals
4. Auto-Categorizer - Suggest categories for subscriptions

All features include caching to optimize API usage.
"""
import json
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Subscription, Customer, Category, Group
from app.ai.provider import get_ai_provider, RateLimitError, ServiceUnavailableError, AIProviderError
from app.ai.cache import generate_cache_key, get_cached_response, store_cached_response

logger = logging.getLogger(__name__)


def _parse_json_response(response: str) -> Dict[str, Any]:
    """
    Parse JSON from AI response, handling common formatting issues.
    
    Args:
        response: Raw AI response string
        
    Returns:
        Parsed dictionary or empty dict on failure
    """
    try:
        # Try direct parse first
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object in response
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    logger.warning(f"Failed to parse JSON from response: {response[:200]}...")
    return {}


class SmartAIFeatures:
    """
    AI-powered features for subscription management.
    
    All methods include:
    - Caching to save API quota
    - Error handling with graceful fallbacks
    - Rate limit awareness
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_ai_provider()
    
    # =========================================================================
    # FEATURE 1: SMART LINK INTELLIGENCE
    # =========================================================================
    
    async def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract subscription details from a URL.
        
        This feature analyzes a subscription/pricing page URL and extracts:
        - Vendor name
        - Plan name
        - Cost
        - Billing cycle
        - Currency
        
        Args:
            url: The URL to analyze (e.g., "https://figma.com/pricing")
            
        Returns:
            Dictionary with extracted details or error information
        """
        request_type = "link_intelligence"
        
        # Check cache first
        cache_key = generate_cache_key(request_type, url=url)
        cached = get_cached_response(self.db, cache_key)
        if cached:
            result = _parse_json_response(cached)
            result["cached"] = True
            return result
        
        if not self.provider.is_available():
            return {
                "error": "AI provider not configured",
                "fallback": "Please enter subscription details manually",
                "cached": False
            }
        
        system_prompt = """You are an expert at analyzing subscription and SaaS pricing pages.
Extract pricing information accurately. If you can't determine a value with confidence, use null.
Always respond with valid JSON only, no additional text."""

        prompt = f"""Analyze this subscription/pricing URL and extract the details:

URL: {url}

Based on the URL and your knowledge of this service, extract:
1. The vendor/company name
2. Common plan names and their prices
3. Default billing cycle

Respond with JSON only:
{{
    "vendor_name": "Company name",
    "plan_name": "Most common plan name or null",
    "cost": numeric cost or null,
    "currency": "USD" or appropriate currency code,
    "billing_cycle": "monthly" | "yearly" | "quarterly" | "weekly" | null,
    "confidence": 0-100,
    "notes": "Any relevant notes about pricing",
    "alternative_plans": [
        {{"name": "plan name", "cost": 0, "cycle": "monthly"}}
    ]
}}"""

        try:
            response = await self.provider.generate_completion(
                prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            result = _parse_json_response(response)
            if result:
                result["cached"] = False
                result["url"] = url
                
                # Store in cache
                store_cached_response(
                    self.db, cache_key, request_type, prompt, response
                )
                
                return result
            else:
                return {
                    "error": "Could not parse AI response",
                    "fallback": "Please enter subscription details manually",
                    "cached": False
                }
                
        except RateLimitError as e:
            logger.warning(f"Rate limit hit for link intelligence: {e}")
            return {
                "error": "Daily AI limit reached",
                "message": str(e),
                "fallback": "Please enter subscription details manually",
                "retry_after": "tomorrow",
                "cached": False
            }
        except ServiceUnavailableError as e:
            logger.error(f"Service unavailable for link intelligence: {e}")
            return {
                "error": "AI service temporarily unavailable",
                "message": str(e),
                "fallback": "Please enter subscription details manually",
                "retry_after": "5 minutes",
                "cached": False
            }
        except Exception as e:
            logger.error(f"Error in link intelligence: {e}")
            return {
                "error": "Failed to extract details",
                "message": str(e),
                "fallback": "Please enter subscription details manually",
                "cached": False
            }
    
    # =========================================================================
    # FEATURE 2: BUDGET SURGEON
    # =========================================================================
    
    async def analyze_budget(self, customer_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Identify duplicate or redundant spending across subscriptions.
        
        This feature analyzes all subscriptions and finds:
        - Duplicate vendors
        - Similar/overlapping services
        - Downgrade opportunities
        - Bundle recommendations
        
        Args:
            customer_id: Optional - analyze specific customer or all
            
        Returns:
            Dictionary with savings recommendations
        """
        request_type = "budget_surgeon"
        
        # Get subscriptions
        query = self.db.query(Subscription).filter(Subscription.status == "active")
        if customer_id:
            query = query.filter(Subscription.customer_id == customer_id)
        
        subscriptions = query.all()
        
        if not subscriptions:
            return {
                "message": "No active subscriptions to analyze",
                "duplicates": [],
                "total_potential_savings": 0,
                "current_monthly_total": 0,
                "cached": False
            }
        
        # Prepare subscription data for analysis
        sub_data = []
        total_monthly = 0
        
        for sub in subscriptions:
            monthly_cost = self._normalize_to_monthly(sub.cost, sub.billing_cycle.value)
            total_monthly += monthly_cost
            
            category_name = sub.category.name if sub.category else "Uncategorized"
            
            sub_data.append({
                "id": sub.id,
                "vendor": sub.vendor_name,
                "plan": sub.plan_name or "Standard",
                "cost": sub.cost,
                "cycle": sub.billing_cycle.value,
                "monthly_cost": round(monthly_cost, 2),
                "category": category_name
            })
        
        # Check cache
        cache_key = generate_cache_key(
            request_type, 
            customer_id=customer_id,
            sub_hash=hash(json.dumps(sub_data, sort_keys=True))
        )
        cached = get_cached_response(self.db, cache_key)
        if cached:
            result = _parse_json_response(cached)
            result["cached"] = True
            result["current_monthly_total"] = round(total_monthly, 2)
            return result
        
        if not self.provider.is_available():
            return {
                "error": "AI provider not configured",
                "duplicates": [],
                "total_potential_savings": 0,
                "current_monthly_total": round(total_monthly, 2),
                "cached": False
            }
        
        system_prompt = """You are a subscription cost optimization expert.
Analyze subscriptions to find duplicates, redundancies, and savings opportunities.
Be specific and actionable. Always respond with valid JSON only."""

        prompt = f"""Analyze these subscriptions for cost-saving opportunities:

Current Monthly Total: ${total_monthly:.2f}

Subscriptions:
{json.dumps(sub_data, indent=2)}

Find:
1. Duplicate vendors (same company, multiple subscriptions)
2. Overlapping services (different vendors, similar functionality)
3. Downgrade opportunities (premium plans that could be basic)
4. Bundle opportunities (services that could be combined)

Respond with JSON only:
{{
    "duplicates": [
        {{
            "type": "duplicate_vendor" | "overlapping_service" | "downgrade_opportunity" | "bundle_available",
            "subscriptions": ["vendor1", "vendor2"],
            "subscription_ids": [1, 2],
            "potential_savings": 0.00,
            "recommendation": "Specific action to take",
            "reasoning": "Why this saves money",
            "priority": "high" | "medium" | "low"
        }}
    ],
    "total_potential_savings": 0.00,
    "savings_percentage": 0,
    "summary": "Brief overview of findings"
}}"""

        try:
            response = await self.provider.generate_completion(
                prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=1000
            )
            
            result = _parse_json_response(response)
            if result:
                result["cached"] = False
                result["current_monthly_total"] = round(total_monthly, 2)
                result["subscription_count"] = len(subscriptions)
                
                # Store in cache
                store_cached_response(
                    self.db, cache_key, request_type, prompt, response
                )
                
                return result
            else:
                return {
                    "error": "Could not parse AI response",
                    "duplicates": [],
                    "total_potential_savings": 0,
                    "current_monthly_total": round(total_monthly, 2),
                    "cached": False
                }
                
        except RateLimitError as e:
            return {
                "error": "Daily AI limit reached",
                "message": str(e),
                "duplicates": [],
                "total_potential_savings": 0,
                "current_monthly_total": round(total_monthly, 2),
                "cached": False
            }
        except Exception as e:
            logger.error(f"Error in budget surgeon: {e}")
            return {
                "error": str(e),
                "duplicates": [],
                "total_potential_savings": 0,
                "current_monthly_total": round(total_monthly, 2),
                "cached": False
            }
    
    # =========================================================================
    # FEATURE 3: RENEWAL FORECASTER
    # =========================================================================
    
    async def forecast_renewals(self, months_ahead: int = 12) -> Dict[str, Any]:
        """
        Predict upcoming subscription costs for the next N months.
        
        This feature provides:
        - Month-by-month cost breakdown
        - Peak spending identification
        - Cash flow patterns
        - AI-powered insights
        
        Args:
            months_ahead: Number of months to forecast (default: 12)
            
        Returns:
            Dictionary with forecast data and insights
        """
        request_type = "renewal_forecaster"
        
        # Get all active subscriptions
        subscriptions = self.db.query(Subscription).filter(
            Subscription.status == "active"
        ).all()
        
        if not subscriptions:
            return {
                "message": "No active subscriptions to forecast",
                "forecast": [],
                "total_yearly_cost": 0,
                "cached": False
            }
        
        # Calculate forecast based on renewal dates
        today = date.today()
        forecast = {}
        
        for i in range(months_ahead):
            forecast_date = today + timedelta(days=30 * i)
            month_key = forecast_date.strftime("%Y-%m")
            forecast[month_key] = {
                "month": month_key,
                "month_name": forecast_date.strftime("%B %Y"),
                "cost": 0,
                "subscriptions": [],
                "renewal_count": 0
            }
        
        # Calculate costs for each subscription
        for sub in subscriptions:
            monthly_cost = self._normalize_to_monthly(sub.cost, sub.billing_cycle.value)
            
            # Determine which months this subscription affects
            for i in range(months_ahead):
                forecast_date = today + timedelta(days=30 * i)
                month_key = forecast_date.strftime("%Y-%m")
                
                # Check if renewal falls in this month
                if self._is_renewal_in_month(sub, forecast_date):
                    forecast[month_key]["cost"] += sub.cost
                    forecast[month_key]["subscriptions"].append({
                        "vendor": sub.vendor_name,
                        "cost": sub.cost,
                        "cycle": sub.billing_cycle.value
                    })
                    forecast[month_key]["renewal_count"] += 1
                elif sub.billing_cycle.value == "monthly":
                    # Monthly subscriptions charge every month
                    forecast[month_key]["cost"] += sub.cost
                    forecast[month_key]["subscriptions"].append({
                        "vendor": sub.vendor_name,
                        "cost": sub.cost,
                        "cycle": "monthly"
                    })
        
        # Convert to list and calculate totals
        forecast_list = list(forecast.values())
        total_yearly = sum(m["cost"] for m in forecast_list[:12])
        
        # Find peak spending
        peak_month = max(forecast_list, key=lambda x: x["cost"])
        lowest_month = min(forecast_list, key=lambda x: x["cost"])
        avg_monthly = total_yearly / 12 if forecast_list else 0
        
        # Round all costs
        for month in forecast_list:
            month["cost"] = round(month["cost"], 2)
        
        # Check cache for AI insights
        cache_key = generate_cache_key(
            request_type,
            months=months_ahead,
            sub_count=len(subscriptions),
            total=round(total_yearly, 2)
        )
        
        ai_insights = None
        cached = get_cached_response(self.db, cache_key)
        
        if cached:
            ai_insights = _parse_json_response(cached)
        elif self.provider.is_available():
            # Get AI insights on the forecast
            try:
                system_prompt = """You are a financial analyst specializing in subscription management.
Provide actionable insights on spending patterns. Always respond with valid JSON only."""

                prompt = f"""Analyze this {months_ahead}-month subscription forecast:

Total Yearly Cost: ${total_yearly:.2f}
Average Monthly: ${avg_monthly:.2f}
Peak Month: {peak_month['month_name']} (${peak_month['cost']:.2f})
Lowest Month: {lowest_month['month_name']} (${lowest_month['cost']:.2f})
Total Subscriptions: {len(subscriptions)}

Monthly Breakdown:
{json.dumps(forecast_list[:6], indent=2)}

Provide insights in JSON:
{{
    "insights": ["key observation 1", "key observation 2"],
    "recommendations": ["actionable recommendation 1", "recommendation 2"],
    "spending_pattern": "consistent" | "variable" | "seasonal",
    "risk_level": "low" | "medium" | "high",
    "optimization_tip": "One key tip to optimize spending"
}}"""

                response = await self.provider.generate_completion(
                    prompt,
                    system_prompt=system_prompt,
                    temperature=0.6,
                    max_tokens=400
                )
                
                ai_insights = _parse_json_response(response)
                if ai_insights:
                    store_cached_response(
                        self.db, cache_key, request_type, prompt, response
                    )
                    
            except Exception as e:
                logger.error(f"Error getting forecast insights: {e}")
        
        return {
            "forecast": forecast_list,
            "total_yearly_cost": round(total_yearly, 2),
            "average_monthly_cost": round(avg_monthly, 2),
            "peak_spending": {
                "month": peak_month["month_name"],
                "amount": round(peak_month["cost"], 2)
            },
            "lowest_spending": {
                "month": lowest_month["month_name"],
                "amount": round(lowest_month["cost"], 2)
            },
            "subscription_count": len(subscriptions),
            "ai_insights": ai_insights,
            "cached": cached is not None
        }
    
    # =========================================================================
    # FEATURE 4: AUTO-CATEGORIZER
    # =========================================================================
    
    async def suggest_category(
        self, 
        vendor_name: str, 
        plan_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest the best category for a subscription.
        
        This feature:
        - Analyzes vendor name and plan
        - Matches against existing categories
        - Provides confidence score
        - Suggests alternatives
        
        Args:
            vendor_name: Name of the subscription vendor
            plan_name: Optional plan name for better matching
            
        Returns:
            Dictionary with category suggestion and confidence
        """
        request_type = "auto_categorizer"
        
        # Check cache first
        cache_key = generate_cache_key(
            request_type, 
            vendor=vendor_name.lower().strip(),
            plan=(plan_name or "").lower().strip()
        )
        cached = get_cached_response(self.db, cache_key)
        if cached:
            result = _parse_json_response(cached)
            result["cached"] = True
            return result
        
        # Get available categories
        categories = self.db.query(Category).all()
        if not categories:
            return {
                "suggested_category": "Uncategorized",
                "suggested_category_id": None,
                "confidence": 0,
                "reasoning": "No categories available in the system",
                "alternatives": [],
                "cached": False
            }
        
        category_list = [
            {"id": cat.id, "name": cat.name, "description": cat.description or ""}
            for cat in categories
        ]
        
        if not self.provider.is_available():
            # Return first category as fallback
            return {
                "suggested_category": categories[0].name,
                "suggested_category_id": categories[0].id,
                "confidence": 0,
                "reasoning": "AI provider not available - default suggestion",
                "alternatives": [],
                "cached": False
            }
        
        system_prompt = """You are an expert at categorizing software subscriptions and services.
Analyze the vendor name and suggest the most appropriate category.
Always respond with valid JSON only."""

        prompt = f"""Categorize this subscription:

Vendor: {vendor_name}
Plan: {plan_name or 'Not specified'}

Available categories:
{json.dumps(category_list, indent=2)}

Choose the best matching category from the list above.
Provide a confidence score (0-100) and reasoning.

Respond with JSON only:
{{
    "suggested_category": "exact category name from list",
    "suggested_category_id": category_id_number,
    "confidence": 0-100,
    "reasoning": "Brief explanation of why this category fits",
    "alternatives": [
        {{"category": "name", "category_id": id, "confidence": 0-100}}
    ]
}}"""

        try:
            response = await self.provider.generate_completion(
                prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=300
            )
            
            result = _parse_json_response(response)
            if result:
                result["cached"] = False
                result["vendor_name"] = vendor_name
                
                # Validate suggested category exists
                suggested = result.get("suggested_category", "")
                valid_category = next(
                    (c for c in categories if c.name.lower() == suggested.lower()),
                    None
                )
                
                if valid_category:
                    result["suggested_category"] = valid_category.name
                    result["suggested_category_id"] = valid_category.id
                else:
                    # Fallback to first category
                    result["suggested_category"] = categories[0].name
                    result["suggested_category_id"] = categories[0].id
                    result["confidence"] = max(0, result.get("confidence", 0) - 30)
                
                # Store in cache
                store_cached_response(
                    self.db, cache_key, request_type, prompt, response
                )
                
                return result
            else:
                return {
                    "suggested_category": categories[0].name,
                    "suggested_category_id": categories[0].id,
                    "confidence": 0,
                    "reasoning": "Could not parse AI response",
                    "alternatives": [],
                    "cached": False
                }
                
        except RateLimitError as e:
            return {
                "error": "Daily AI limit reached",
                "suggested_category": categories[0].name,
                "suggested_category_id": categories[0].id,
                "confidence": 0,
                "reasoning": str(e),
                "alternatives": [],
                "cached": False
            }
        except Exception as e:
            logger.error(f"Error in auto-categorizer: {e}")
            return {
                "error": str(e),
                "suggested_category": categories[0].name,
                "suggested_category_id": categories[0].id,
                "confidence": 0,
                "reasoning": f"Error: {str(e)}",
                "alternatives": [],
                "cached": False
            }
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _normalize_to_monthly(self, cost: float, cycle: str) -> float:
        """Convert any billing cycle cost to monthly equivalent."""
        cycle_multipliers = {
            "weekly": 4.33,
            "monthly": 1,
            "quarterly": 1/3,
            "biannual": 1/6,
            "yearly": 1/12
        }
        return cost * cycle_multipliers.get(cycle, 1)
    
    def _is_renewal_in_month(self, sub: Subscription, target_date: date) -> bool:
        """Check if a subscription renews in the target month."""
        if not sub.next_renewal_date:
            return False
        
        return (
            sub.next_renewal_date.year == target_date.year and
            sub.next_renewal_date.month == target_date.month
        )
