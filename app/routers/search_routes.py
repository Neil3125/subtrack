"""Search routes with HTML responses for HTMX."""
from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models import Category, Group, Customer, Subscription

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/search", response_class=HTMLResponse)
async def search_html(request: Request, q: str = Query("", min_length=0, alias="search_query_field"), db: Session = Depends(get_db)):
    """Search with HTML response for HTMX."""
    if not q or len(q) < 2:
        return ""
    
    search_term = f"%{q.lower()}%"
    
    # Search categories
    categories = db.query(Category).filter(
        or_(
            func.lower(Category.name).like(search_term),
            func.lower(Category.description).like(search_term)
        )
    ).limit(5).all()
    
    # Search groups
    groups = db.query(Group).filter(
        or_(
            func.lower(Group.name).like(search_term),
            func.lower(Group.notes).like(search_term)
        )
    ).limit(5).all()
    
    # Search customers
    customers = db.query(Customer).filter(
        or_(
            func.lower(Customer.name).like(search_term),
            func.lower(Customer.email).like(search_term),
            func.lower(Customer.tags).like(search_term),
            func.lower(Customer.notes).like(search_term)
        )
    ).limit(5).all()
    
    # Search subscriptions
    subscriptions = db.query(Subscription).filter(
        or_(
            func.lower(Subscription.vendor_name).like(search_term),
            func.lower(Subscription.plan_name).like(search_term),
            func.lower(Subscription.notes).like(search_term)
        )
    ).limit(5).all()
    
    return templates.TemplateResponse("components/search_results.html", {
        "request": request,
        "query": q,
        "categories": categories,
        "groups": groups,
        "customers": customers,
        "subscriptions": subscriptions,
        "total": len(categories) + len(groups) + len(customers) + len(subscriptions)
    })
