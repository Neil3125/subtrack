"""AI-powered routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.ai.provider import get_ai_provider
from app.ai.insights import InsightsAnalyzer
from app.ai.link_intelligence import LinkAnalyzer
from app.ai.features import AIFeatures
from app.ai.smart_features import SmartAIFeatures
from app.ai.cache import get_cache_stats, clear_expired_cache
from app.models import Link
from app.models.link import UserDecision
from app.schemas import LinkResponse, LinkDecision

router = APIRouter()


class InsightsRequest(BaseModel):
    """Request schema for insights."""
    category_id: Optional[int] = None
    group_id: Optional[int] = None
    customer_id: Optional[int] = None
    threshold_days: int = 30


class LinkAnalyzeRequest(BaseModel):
    """Request schema for link analysis."""
    run_ai_refinement: bool = True


@router.post("/insights")
async def get_insights(request: InsightsRequest, db: Session = Depends(get_db)):
    """Generate AI-powered insights about subscriptions."""
    ai_provider = get_ai_provider()
    analyzer = InsightsAnalyzer(db, ai_provider)
    
    insights = await analyzer.generate_insights(
        category_id=request.category_id,
        group_id=request.group_id,
        customer_id=request.customer_id,
        threshold_days=request.threshold_days
    )
    
    return insights


@router.post("/link_analyze")
@router.post("/analyze-links")
async def analyze_links(request: LinkAnalyzeRequest = None, db: Session = Depends(get_db)):
    """Analyze and discover relationships between entities."""
    ai_provider = get_ai_provider()
    analyzer = LinkAnalyzer(db, ai_provider)
    
    # Default request if none provided
    if request is None:
        request = LinkAnalyzeRequest(run_ai_refinement=False)
    
    # Run all link analyses
    customer_links = analyzer.analyze_customer_links()
    subscription_links = analyzer.analyze_subscription_links()
    cross_category_links = analyzer.analyze_cross_category_links()
    
    # Combine all links
    all_links = customer_links + subscription_links + cross_category_links
    
    # Refine with AI if requested
    if request.run_ai_refinement and ai_provider.is_available():
        all_links = await analyzer.refine_with_ai(all_links)
    
    # Store links in database (only new ones)
    new_links = []
    for link_data in all_links:
        # Check if link already exists
        existing = db.query(Link).filter(
            Link.source_type == link_data['source_type'],
            Link.source_id == link_data['source_id'],
            Link.target_type == link_data['target_type'],
            Link.target_id == link_data['target_id']
        ).first()
        
        if not existing:
            db_link = Link(**link_data)
            db.add(db_link)
            new_links.append(db_link)
    
    if new_links:
        db.commit()
        for link in new_links:
            db.refresh(link)
    
    return {
        'total_analyzed': len(all_links),
        'new_links_found': len(new_links),
        'links_found': len(new_links),
        'links': [LinkResponse.model_validate(link) for link in new_links]
    }


@router.get("/links")
def get_links(
    source_type: Optional[str] = None,
    source_id: Optional[int] = None,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    pending_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get links with optional filters."""
    query = db.query(Link)
    
    if source_type:
        query = query.filter(Link.source_type == source_type)
    if source_id:
        query = query.filter(Link.source_id == source_id)
    if target_type:
        query = query.filter(Link.target_type == target_type)
    if target_id:
        query = query.filter(Link.target_id == target_id)
    if pending_only:
        query = query.filter(Link.user_decision.is_(None))
    
    links = query.order_by(Link.confidence.desc()).all()
    return [LinkResponse.model_validate(link) for link in links]


@router.post("/links/{link_id}/decide")
def decide_on_link(link_id: int, decision: LinkDecision, db: Session = Depends(get_db)):
    """Accept or reject a link suggestion."""
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    link.user_decision = decision.decision
    db.commit()
    db.refresh(link)
    
    return LinkResponse.model_validate(link)


@router.delete("/links/{link_id}")
def unlink(link_id: int, db: Session = Depends(get_db)):
    """Remove/unlink a connection."""
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(link)
    db.commit()
    return {"message": "Link removed successfully", "id": link_id}


# ==================== AI Features Routes ====================

@router.post("/categorize")
async def smart_categorization(data: dict, db: Session = Depends(get_db)):
    """Smart subscription categorization."""
    ai_features = AIFeatures(db)
    result = await ai_features.smart_categorization(
        data.get("subscription_name", ""),
        data.get("plan_name")
    )
    return result


@router.get("/optimize-costs")
async def cost_optimization(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get cost optimization suggestions."""
    ai_features = AIFeatures(db)
    result = await ai_features.cost_optimization(customer_id)
    return result


@router.get("/renewal-reminders")
async def renewal_reminders(days_ahead: int = 30, db: Session = Depends(get_db)):
    """Get smart renewal reminders."""
    ai_features = AIFeatures(db)
    reminders = await ai_features.smart_renewal_reminders(days_ahead)
    return {"reminders": reminders}


@router.get("/detect-duplicates")
async def detect_duplicates(db: Session = Depends(get_db)):
    """Detect duplicate or overlapping subscriptions."""
    ai_features = AIFeatures(db)
    duplicates = await ai_features.duplicate_detection()
    return {"duplicates": duplicates}


@router.get("/usage-patterns/{customer_id}")
async def usage_patterns(customer_id: int, db: Session = Depends(get_db)):
    """Analyze customer usage patterns."""
    ai_features = AIFeatures(db)
    analysis = await ai_features.usage_pattern_analysis(customer_id)
    return analysis


@router.get("/forecast-budget")
async def forecast_budget(months_ahead: int = 12, db: Session = Depends(get_db)):
    """Forecast future budget needs."""
    ai_features = AIFeatures(db)
    forecast = await ai_features.budget_forecasting(months_ahead)
    return forecast


@router.post("/smart-tags/{subscription_id}")
async def generate_smart_tags(subscription_id: int, db: Session = Depends(get_db)):
    """Generate smart tags for a subscription."""
    ai_features = AIFeatures(db)
    tags = await ai_features.smart_tagging(subscription_id)
    return {"tags": tags}


@router.post("/search")
async def natural_language_search(data: dict, db: Session = Depends(get_db)):
    """Natural language search for subscriptions."""
    ai_features = AIFeatures(db)
    results = await ai_features.natural_language_search(data.get("query", ""))
    return results


@router.get("/health-score/{subscription_id}")
async def subscription_health(subscription_id: int, db: Session = Depends(get_db)):
    """Get subscription health score."""
    ai_features = AIFeatures(db)
    health = await ai_features.subscription_health_score(subscription_id)
    return health


# ==================== NEW SMART AI FEATURES (OpenRouter) ====================

class ExtractURLRequest(BaseModel):
    """Request schema for URL extraction."""
    url: str


class BudgetSurgeonRequest(BaseModel):
    """Request schema for budget analysis."""
    customer_id: Optional[int] = None


class RenewalForecastRequest(BaseModel):
    """Request schema for renewal forecast."""
    months_ahead: int = 12


class AutoCategorizeRequest(BaseModel):
    """Request schema for auto-categorization."""
    vendor_name: str
    plan_name: Optional[str] = None


@router.post("/extract-from-url")
async def extract_from_url(request: ExtractURLRequest, db: Session = Depends(get_db)):
    """
    🔗 Smart Link Intelligence
    
    Extract subscription details from a URL automatically.
    """
    from fastapi.responses import HTMLResponse
    from fastapi.templating import Jinja2Templates
    
    smart_features = SmartAIFeatures(db)
    result = await smart_features.extract_from_url(request.url)
    
    # Render as HTML for HTMX
    templates = Jinja2Templates(directory="app/templates")
    html = f"""
    <div class="ai-result {'ai-result-error' if result.get('error') else 'ai-result-success'}">
        {'<div class="ai-error"><span class="ai-error-icon">⚠️</span><div><strong>' + result.get('error', '') + '</strong>' + ('<p class="text-sm text-secondary">' + result.get('fallback', '') + '</p>' if result.get('fallback') else '') + '</div></div>' if result.get('error') else ''}
        {'' if result.get('error') else f'''
        <div class="ai-success">
            <div class="ai-result-header">
                <span class="ai-confidence-badge confidence-{'high' if result.get('confidence', 0) > 80 else 'medium' if result.get('confidence', 0) > 50 else 'low'}">
                    {result.get('confidence', 0)}% confidence
                </span>
                {'<span class="ai-cached-badge">⚡ Cached</span>' if result.get('cached') else ''}
            </div>
            <div class="ai-extracted-data">
                <div class="ai-data-row">
                    <span class="ai-data-label">Vendor:</span>
                    <span class="ai-data-value">{result.get('vendor_name', 'Unknown')}</span>
                </div>
                <div class="ai-data-row">
                    <span class="ai-data-label">Plan:</span>
                    <span class="ai-data-value">{result.get('plan_name', 'Standard')}</span>
                </div>
                <div class="ai-data-row">
                    <span class="ai-data-label">Cost:</span>
                    <span class="ai-data-value">${result.get('cost', '0')} {result.get('currency', 'USD')}</span>
                </div>
                <div class="ai-data-row">
                    <span class="ai-data-label">Billing:</span>
                    <span class="ai-data-value">{result.get('billing_cycle', 'monthly')}</span>
                </div>
                {'<div class="ai-data-row"><span class="ai-data-label">Notes:</span><span class="ai-data-value text-secondary">' + result.get('notes', '') + '</span></div>' if result.get('notes') else ''}
            </div>
        </div>
        '''}
    </div>
    """
    return HTMLResponse(content=html)


@router.post("/budget-surgeon")
async def budget_surgeon(
    request: BudgetSurgeonRequest = None, 
    db: Session = Depends(get_db)
):
    """
    🔪 Budget Surgeon
    
    Identify duplicate or redundant spending across subscriptions.
    """
    from fastapi.responses import HTMLResponse
    
    if request is None:
        request = BudgetSurgeonRequest()
    
    smart_features = SmartAIFeatures(db)
    result = await smart_features.analyze_budget(request.customer_id)
    
    # Build HTML response
    if result.get('error'):
        html = f"""
        <div class="ai-result ai-result-error">
            <div class="ai-error">
                <span class="ai-error-icon">⚠️</span>
                <div>
                    <strong>{result.get('error')}</strong>
                    {f'<p class="text-sm text-secondary">{result.get("message")}</p>' if result.get('message') else ''}
                </div>
            </div>
        </div>
        """
    else:
        duplicates_html = ""
        if result.get('duplicates') and len(result['duplicates']) > 0:
            duplicates_html = "<h5>Recommendations:</h5>"
            for item in result['duplicates']:
                priority = item.get('priority', 'medium')
                duplicates_html += f"""
                <div class="ai-recommendation-card priority-{priority}">
                    <div class="ai-rec-header">
                        <span class="ai-rec-type">{item.get('type', '').replace('_', ' ').title()}</span>
                        <span class="ai-rec-savings">${item.get('potential_savings', 0):.2f}/mo</span>
                    </div>
                    <p class="ai-rec-action">{item.get('recommendation', '')}</p>
                    <p class="ai-rec-reason text-sm text-secondary">{item.get('reasoning', '')}</p>
                </div>
                """
        else:
            duplicates_html = """
            <div class="ai-no-issues">
                <span class="ai-success-icon">✅</span>
                <p>No duplicate or redundant subscriptions found. Your subscription portfolio looks optimized!</p>
            </div>
            """
        
        html = f"""
        <div class="ai-result ai-result-success">
            <div class="ai-success">
                <div class="ai-result-header">
                    <div class="ai-savings-highlight">
                        <span class="ai-savings-amount">${result.get('total_potential_savings', 0):.2f}</span>
                        <span class="ai-savings-label">potential monthly savings</span>
                    </div>
                    {f'<span class="ai-cached-badge">⚡ Cached</span>' if result.get('cached') else ''}
                </div>
                <div class="ai-summary mb-3">
                    <p><strong>Current Monthly:</strong> ${result.get('current_monthly_total', 0):.2f}</p>
                    {f'<p class="text-secondary">{result.get("summary")}</p>' if result.get('summary') else ''}
                </div>
                <div class="ai-recommendations">
                    {duplicates_html}
                </div>
            </div>
        </div>
        """
    
    return HTMLResponse(content=html)


@router.post("/renewal-forecast")
async def renewal_forecast(
    request: RenewalForecastRequest = None,
    db: Session = Depends(get_db)
):
    """
    📅 Renewal Forecaster
    
    Predict upcoming subscription costs for the next N months.
    """
    from fastapi.responses import HTMLResponse
    
    if request is None:
        request = RenewalForecastRequest()
    
    smart_features = SmartAIFeatures(db)
    result = await smart_features.forecast_renewals(request.months_ahead)
    
    # Build HTML response
    if result.get('error'):
        html = f"""
        <div class="ai-result ai-result-error">
            <div class="ai-error">
                <span class="ai-error-icon">⚠️</span>
                <div><strong>{result.get('error')}</strong></div>
            </div>
        </div>
        """
    else:
        # Build forecast chart
        forecast_bars = ""
        peak_amount = result.get('peak_spending', {}).get('amount', 1)
        if peak_amount == 0:
            peak_amount = 1
        
        for month in result.get('forecast', [])[:12]:
            month_cost = month.get('cost', 0)
            height = int((month_cost / peak_amount * 100)) if peak_amount > 0 else 0
            month_num = month.get('month', '')[-2:]
            forecast_bars += f"""
            <div class="forecast-bar-container" title="{month.get('month_name', '')}: ${month_cost:.2f}">
                <div class="forecast-bar" style="height: {height}%;"></div>
                <span class="forecast-month">{month_num}</span>
            </div>
            """
        
        # Build AI insights
        insights_html = ""
        if result.get('ai_insights'):
            insights_list = ""
            for insight in result.get('ai_insights', {}).get('insights', []):
                insights_list += f"<li>{insight}</li>"
            
            opt_tip = result.get('ai_insights', {}).get('optimization_tip', '')
            
            insights_html = f"""
            <div class="ai-insights-section">
                <h5>🤖 AI Insights:</h5>
                {f'<ul class="ai-insights-list">{insights_list}</ul>' if insights_list else ''}
                {f'<div class="ai-tip"><strong>💡 Tip:</strong> {opt_tip}</div>' if opt_tip else ''}
            </div>
            """
        
        html = f"""
        <div class="ai-result ai-result-success">
            <div class="ai-success">
                <div class="ai-forecast-summary">
                    <div class="ai-forecast-stat">
                        <span class="ai-forecast-value">${result.get('total_yearly_cost', 0):.2f}</span>
                        <span class="ai-forecast-label">Yearly Total</span>
                    </div>
                    <div class="ai-forecast-stat">
                        <span class="ai-forecast-value">${result.get('average_monthly_cost', 0):.2f}</span>
                        <span class="ai-forecast-label">Avg Monthly</span>
                    </div>
                    <div class="ai-forecast-stat">
                        <span class="ai-forecast-value">{result.get('subscription_count', 0)}</span>
                        <span class="ai-forecast-label">Subscriptions</span>
                    </div>
                </div>
                
                {f'''<div class="ai-peak-info">
                    <p>📈 <strong>Peak:</strong> {result.get('peak_spending', {}).get('month')} (${result.get('peak_spending', {}).get('amount', 0):.2f})</p>
                    <p>📉 <strong>Lowest:</strong> {result.get('lowest_spending', {}).get('month')} (${result.get('lowest_spending', {}).get('amount', 0):.2f})</p>
                </div>''' if result.get('peak_spending') else ''}
                
                {f'<div class="ai-forecast-chart"><h5>12-Month Forecast:</h5><div class="forecast-bars">{forecast_bars}</div></div>' if result.get('forecast') else ''}
                
                {insights_html}
            </div>
        </div>
        """
    
    return HTMLResponse(content=html)


@router.post("/categorize-subscription")
async def categorize_subscription(
    request: AutoCategorizeRequest,
    db: Session = Depends(get_db)
):
    """
    📁 Auto-Categorizer
    
    Suggest the best category for a subscription.
    """
    from fastapi.responses import HTMLResponse
    
    smart_features = SmartAIFeatures(db)
    result = await smart_features.suggest_category(
        request.vendor_name,
        request.plan_name
    )
    
    # Build HTML response
    if result.get('error') and not result.get('suggested_category'):
        html = f"""
        <div class="ai-result ai-result-error">
            <div class="ai-error">
                <span class="ai-error-icon">⚠️</span>
                <div><strong>{result.get('error')}</strong></div>
            </div>
        </div>
        """
    else:
        # Build alternatives
        alternatives_html = ""
        if result.get('alternatives') and len(result.get('alternatives', [])) > 0:
            alternatives_html = '<p class="text-sm text-secondary mb-1">Alternatives:</p>'
            for alt in result['alternatives']:
                alternatives_html += f'<span class="ai-alt-badge">{alt.get("category")} ({alt.get("confidence")}%)</span>'
        
        confidence = result.get('confidence', 0)
        confidence_class = 'high' if confidence > 80 else 'medium' if confidence > 50 else 'low'
        
        html = f"""
        <div class="ai-result ai-result-success">
            <div class="ai-success">
                <div class="ai-result-header">
                    <span class="ai-confidence-badge confidence-{confidence_class}">
                        {confidence}% confidence
                    </span>
                    {f'<span class="ai-cached-badge">⚡ Cached</span>' if result.get('cached') else ''}
                </div>
                <div class="ai-category-suggestion">
                    <div class="ai-suggested-category">
                        <span class="ai-category-icon">📁</span>
                        <span class="ai-category-name">{result.get('suggested_category', 'Uncategorized')}</span>
                    </div>
                    {f'<p class="ai-reasoning text-secondary">{result.get("reasoning")}</p>' if result.get('reasoning') else ''}
                </div>
                {f'<div class="ai-alternatives">{alternatives_html}</div>' if alternatives_html else ''}
            </div>
        </div>
        """
    
    return HTMLResponse(content=html)


# ==================== CACHE MANAGEMENT ====================

@router.get("/cache/stats")
async def get_ai_cache_stats(db: Session = Depends(get_db)):
    """
    Get AI cache statistics.
    
    Returns cache hit rates, entry counts, and usage by feature type.
    """
    from fastapi.responses import HTMLResponse
    
    stats = get_cache_stats(db)
    
    # Build stats HTML
    by_type_html = ""
    if stats.get('by_type'):
        for req_type, data in stats['by_type'].items():
            by_type_html += f"""
            <div class="cache-stat-item">
                <span class="cache-stat-label">{req_type.replace('_', ' ').title()}:</span>
                <span class="cache-stat-value">{data['count']} entries ({data['hits']} hits)</span>
            </div>
            """
    
    html = f"""
    <div class="cache-stats-container">
        <div class="cache-stat-grid">
            <div class="cache-stat-card">
                <div class="cache-stat-number">{stats.get('total_entries', 0)}</div>
                <div class="cache-stat-text">Total Entries</div>
            </div>
            <div class="cache-stat-card">
                <div class="cache-stat-number">{stats.get('active_entries', 0)}</div>
                <div class="cache-stat-text">Active</div>
            </div>
            <div class="cache-stat-card">
                <div class="cache-stat-number">{stats.get('expired_entries', 0)}</div>
                <div class="cache-stat-text">Expired</div>
            </div>
            <div class="cache-stat-card">
                <div class="cache-stat-number">{stats.get('cache_ttl_hours', 24):.0f}h</div>
                <div class="cache-stat-text">Cache TTL</div>
            </div>
        </div>
        {f'<div class="cache-by-type mt-4"><h5>By Feature Type:</h5>{by_type_html}</div>' if by_type_html else ''}
    </div>
    <style>
    .cache-stats-container {{ margin-top: 1rem; }}
    .cache-stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }}
    .cache-stat-card {{ text-align: center; padding: 1rem; background: var(--color-background); border-radius: var(--border-radius); border: 1px solid var(--color-border); }}
    .cache-stat-number {{ font-size: 1.75rem; font-weight: 700; color: var(--color-primary); }}
    .cache-stat-text {{ font-size: 0.75rem; color: var(--color-text-secondary); margin-top: 0.25rem; }}
    .cache-by-type h5 {{ font-size: 0.875rem; margin-bottom: 0.5rem; }}
    .cache-stat-item {{ display: flex; justify-content: space-between; padding: 0.5rem; background: var(--color-background); border-radius: var(--border-radius); margin-bottom: 0.5rem; }}
    .cache-stat-label {{ color: var(--color-text-secondary); font-size: 0.875rem; }}
    .cache-stat-value {{ font-weight: 500; font-size: 0.875rem; }}
    @media (max-width: 768px) {{ .cache-stat-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    </style>
    """
    
    return HTMLResponse(content=html)


@router.post("/cache/clear-expired")
async def clear_ai_expired_cache(db: Session = Depends(get_db)):
    """
    Clear expired cache entries.
    
    This frees up database space without affecting active cache entries.
    """
    from fastapi.responses import HTMLResponse
    
    deleted = clear_expired_cache(db)
    
    # Return updated stats
    stats = get_cache_stats(db)
    
    # Build stats HTML (same as get_cache_stats)
    by_type_html = ""
    if stats.get('by_type'):
        for req_type, data in stats['by_type'].items():
            by_type_html += f"""
            <div class="cache-stat-item">
                <span class="cache-stat-label">{req_type.replace('_', ' ').title()}:</span>
                <span class="cache-stat-value">{data['count']} entries ({data['hits']} hits)</span>
            </div>
            """
    
    html = f"""
    <div class="cache-stats-container">
        <div class="alert alert-success mb-3">✓ Cleared {deleted} expired cache entries</div>
        <div class="cache-stat-grid">
            <div class="cache-stat-card">
                <div class="cache-stat-number">{stats.get('total_entries', 0)}</div>
                <div class="cache-stat-text">Total Entries</div>
            </div>
            <div class="cache-stat-card">
                <div class="cache-stat-number">{stats.get('active_entries', 0)}</div>
                <div class="cache-stat-text">Active</div>
            </div>
            <div class="cache-stat-card">
                <div class="cache-stat-number">{stats.get('expired_entries', 0)}</div>
                <div class="cache-stat-text">Expired</div>
            </div>
            <div class="cache-stat-card">
                <div class="cache-stat-number">{stats.get('cache_ttl_hours', 24):.0f}h</div>
                <div class="cache-stat-text">Cache TTL</div>
            </div>
        </div>
        {f'<div class="cache-by-type mt-4"><h5>By Feature Type:</h5>{by_type_html}</div>' if by_type_html else ''}
    </div>
    <style>
    .cache-stats-container {{ margin-top: 1rem; }}
    .cache-stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }}
    .cache-stat-card {{ text-align: center; padding: 1rem; background: var(--color-background); border-radius: var(--border-radius); border: 1px solid var(--color-border); }}
    .cache-stat-number {{ font-size: 1.75rem; font-weight: 700; color: var(--color-primary); }}
    .cache-stat-text {{ font-size: 0.75rem; color: var(--color-text-secondary); margin-top: 0.25rem; }}
    .cache-by-type h5 {{ font-size: 0.875rem; margin-bottom: 0.5rem; }}
    .cache-stat-item {{ display: flex; justify-content: space-between; padding: 0.5rem; background: var(--color-background); border-radius: var(--border-radius); margin-bottom: 0.5rem; }}
    .cache-stat-label {{ color: var(--color-text-secondary); font-size: 0.875rem; }}
    .cache-stat-value {{ font-weight: 500; font-size: 0.875rem; }}
    .alert {{ padding: 0.75rem 1rem; border-radius: var(--border-radius); }}
    .alert-success {{ background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: var(--color-success); }}
    @media (max-width: 768px) {{ .cache-stat-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    </style>
    """
    
    return HTMLResponse(content=html)


@router.get("/status")
@router.get("/test-ai-direct")
async def test_ai_direct():
    """Direct test of AI API - bypasses cache and shows real usage."""
    from app.ai.provider import get_ai_provider
    import time
    
    provider = get_ai_provider()
    
    result = {
        "provider_type": type(provider).__name__,
        "is_available": provider.is_available(),
        "config": {}
    }
    
    if hasattr(provider, 'api_key'):
        result["config"]["api_key"] = provider.api_key[:20] + "..."
    if hasattr(provider, 'model'):
        result["config"]["model"] = provider.model
    if hasattr(provider, 'base_url'):
        result["config"]["base_url"] = provider.base_url
    
    if not provider.is_available():
        result["status"] = "AI not configured"
        return result
    
    try:
        start = time.time()
        response = await provider.generate_completion(
            prompt="In exactly 10 words, describe what SubTrack subscription manager does.",
            temperature=0.7,
            max_tokens=50
        )
        end = time.time()
        
        result["status"] = "success"
        result["response"] = response
        result["time_taken"] = f"{end - start:.2f}s"
        result["message"] = "✅ AI API is working! This call used your OpenRouter quota."
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = "API call failed - see error for details"
    
    return result


async def get_ai_status(db: Session = Depends(get_db)):
    """
    Get AI provider status and configuration.
    """
    from fastapi.responses import HTMLResponse
    from app.config import settings
    from app.ai.provider import get_ai_provider
    
    provider = get_ai_provider()
    is_available = provider.is_available()
    
    html = f"""
    <div class="ai-status-badge {'ai-online' if is_available else 'ai-offline'}">
        <span>{'✓' if is_available else '✗'}</span>
        <span>{settings.subtrack_ai_provider.title()} - {'Online' if is_available else 'Offline'}</span>
        <span style="opacity: 0.7; font-size: 0.7rem;">({settings.ai_daily_limit} req/day)</span>
    </div>
    """
    
    return HTMLResponse(content=html)
