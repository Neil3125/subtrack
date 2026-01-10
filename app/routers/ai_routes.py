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
async def analyze_links(request: LinkAnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze and discover relationships between entities."""
    ai_provider = get_ai_provider()
    analyzer = LinkAnalyzer(db, ai_provider)
    
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
