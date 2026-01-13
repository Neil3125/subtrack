"""Web routes for rendering HTML templates."""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.database import get_db
from app.models import Category, Group, Customer, Subscription, Link, User
from app.models.subscription import SubscriptionStatus
from app.routers.auth_routes import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Render dashboard."""
    # Get categories for sidebar
    categories = db.query(Category).all()
    
    # Get stats
    total_active = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).count()
    
    # Calculate monthly cost and annual revenue
    subscriptions = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).all()
    monthly_cost = sum(sub.cost for sub in subscriptions)
    
    # Calculate annual revenue based on billing cycles
    annual_revenue = 0
    for sub in subscriptions:
        if sub.billing_cycle.value == 'monthly':
            annual_revenue += sub.cost * 12
        elif sub.billing_cycle.value == 'yearly':
            annual_revenue += sub.cost
        elif sub.billing_cycle.value == 'quarterly':
            annual_revenue += sub.cost * 4
        elif sub.billing_cycle.value == 'weekly':
            annual_revenue += sub.cost * 52
        elif sub.billing_cycle.value == 'biannual':
            annual_revenue += sub.cost * 2
        else:
            annual_revenue += sub.cost * 12  # Default to monthly
    
    # Get expiring soon
    today = date.today()
    threshold_date = today + timedelta(days=30)
    expiring_soon = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.next_renewal_date <= threshold_date,
        Subscription.next_renewal_date >= today
    ).all()
    
    # Get overdue
    overdue = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.next_renewal_date < today
    ).all()
    
    # Get all active subscriptions for the modal
    all_active = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).all()
    
    stats = {
        'total_active': total_active,
        'monthly_cost': monthly_cost,
        'annual_revenue': annual_revenue,
        'expiring_soon': len(expiring_soon),
        'overdue': len(overdue)
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "categories": categories,
        "stats": stats,
        "expiring_soon": expiring_soon,
        "overdue": overdue,
        "all_active": all_active,
        "insights": None
    })


@router.get("/categories", response_class=HTMLResponse)
async def categories_list(request: Request, db: Session = Depends(get_db)):
    """List all categories."""
    categories = db.query(Category).all()
    
    return templates.TemplateResponse("categories_list.html", {
        "request": request,
        "categories": categories
    })


@router.get("/groups", response_class=HTMLResponse)
async def groups_list(request: Request, db: Session = Depends(get_db)):
    """List all groups."""
    categories = db.query(Category).all()
    groups = db.query(Group).all()
    
    return templates.TemplateResponse("categories_list.html", {
        "request": request,
        "categories": categories,
        "groups": groups
    })


@router.get("/subscriptions", response_class=HTMLResponse)
async def subscriptions_page(request: Request, db: Session = Depends(get_db)):
    """Subscriptions management page."""
    categories = db.query(Category).all()
    subscriptions = db.query(Subscription).all()
    
    # Calculate stats
    total_subscriptions = len(subscriptions)
    active_subs = [s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE]
    active_count = len(active_subs)
    paused_count = len([s for s in subscriptions if s.status == SubscriptionStatus.PAUSED])
    cancelled_count = len([s for s in subscriptions if s.status == SubscriptionStatus.CANCELLED])
    expired_count = len([s for s in subscriptions if s.status == SubscriptionStatus.EXPIRED])
    
    monthly_cost = sum(s.cost for s in active_subs)
    
    # Expiring and overdue
    today = date.today()
    threshold_date = today + timedelta(days=30)
    expiring_soon_count = len([s for s in active_subs if s.next_renewal_date and today <= s.next_renewal_date <= threshold_date])
    overdue_count = len([s for s in active_subs if s.next_renewal_date and s.next_renewal_date < today])
    
    # Category stats
    from collections import defaultdict
    cat_data = defaultdict(lambda: {'count': 0, 'monthly_cost': 0})
    for s in subscriptions:
        cat_data[s.category_id]['count'] += 1
        if s.status == SubscriptionStatus.ACTIVE:
            cat_data[s.category_id]['monthly_cost'] += s.cost
    
    category_stats = []
    for cat in categories:
        if cat.id in cat_data:
            category_stats.append({
                'name': cat.name,
                'count': cat_data[cat.id]['count'],
                'monthly_cost': cat_data[cat.id]['monthly_cost']
            })
    category_stats.sort(key=lambda x: x['count'], reverse=True)
    
    # Cycle stats
    cycle_data = defaultdict(lambda: {'count': 0, 'cost': 0})
    for s in subscriptions:
        cycle_data[s.billing_cycle.value]['count'] += 1
        cycle_data[s.billing_cycle.value]['cost'] += s.cost
    
    return templates.TemplateResponse("subscriptions_page.html", {
        "request": request,
        "categories": categories,
        "subscriptions": subscriptions,
        "total_subscriptions": total_subscriptions,
        "active_count": active_count,
        "paused_count": paused_count,
        "cancelled_count": cancelled_count,
        "expired_count": expired_count,
        "monthly_cost": monthly_cost,
        "expiring_soon_count": expiring_soon_count,
        "overdue_count": overdue_count,
        "category_stats": category_stats,
        "cycle_stats": dict(cycle_data)
    })


@router.get("/customers", response_class=HTMLResponse)
async def customers_list(request: Request, db: Session = Depends(get_db)):
    """List all customers with statistics."""
    categories = db.query(Category).all()
    customers = db.query(Customer).all()
    
    # Calculate statistics
    total_customers = len(customers)
    categories_with_customers = len(set(c.category_id for c in customers))
    unique_countries = list(set(c.country for c in customers if c.country))
    countries_count = len(unique_countries)
    in_groups_count = len([c for c in customers if c.group_id])
    
    # Category breakdown
    from collections import defaultdict
    category_counts = defaultdict(int)
    for c in customers:
        category_counts[c.category_id] += 1
    
    category_breakdown = []
    for cat in categories:
        if cat.id in category_counts:
            category_breakdown.append({
                'name': cat.name,
                'count': category_counts[cat.id]
            })
    category_breakdown.sort(key=lambda x: x['count'], reverse=True)
    
    # Country breakdown
    country_counts = defaultdict(int)
    for c in customers:
        country_counts[c.country or 'Not Specified'] += 1
    
    country_breakdown = [
        {'country': country, 'count': count}
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return templates.TemplateResponse("customers_page.html", {
        "request": request,
        "categories": categories,
        "customers": customers,
        "total_customers": total_customers,
        "categories_count": categories_with_customers,
        "countries_count": countries_count,
        "in_groups_count": in_groups_count,
        "unique_countries": sorted(unique_countries),
        "category_breakdown": category_breakdown,
        "country_breakdown": country_breakdown
    })


@router.get("/subscriptions", response_class=HTMLResponse)
async def subscriptions_list(request: Request, db: Session = Depends(get_db)):
    """List all subscriptions."""
    categories = db.query(Category).all()
    subscriptions = db.query(Subscription).all()
    
    return templates.TemplateResponse("categories_list.html", {
        "request": request,
        "categories": categories,
        "subscriptions": subscriptions
    })


@router.get("/categories/{category_id}", response_class=HTMLResponse)
async def category_detail(category_id: int, request: Request, db: Session = Depends(get_db)):
    """Category detail page."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    # Get all categories for sidebar
    categories = db.query(Category).all()
    
    # Get groups in this category
    groups = db.query(Group).filter(Group.category_id == category_id).all()
    
    # Get customers in this category
    customers = db.query(Customer).filter(Customer.category_id == category_id).all()
    
    # Get subscriptions in this category
    subscriptions = db.query(Subscription).filter(Subscription.category_id == category_id).all()
    
    # Calculate category-specific stats
    today = date.today()
    threshold_date = today + timedelta(days=30)
    
    active_subs = [s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE]
    expiring_soon = len([s for s in active_subs if s.next_renewal_date and today <= s.next_renewal_date <= threshold_date])
    overdue = len([s for s in active_subs if s.next_renewal_date and s.next_renewal_date < today])
    
    category_stats = {
        'expiring_soon': expiring_soon,
        'overdue': overdue
    }
    
    return templates.TemplateResponse("category_detail.html", {
        "request": request,
        "categories": categories,
        "category": category,
        "groups": groups,
        "customers": customers,
        "subscriptions": subscriptions,
        "category_stats": category_stats
    })


@router.get("/groups/{group_id}", response_class=HTMLResponse)
async def group_detail(group_id: int, request: Request, db: Session = Depends(get_db)):
    """Group detail page."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    categories = db.query(Category).all()
    customers = db.query(Customer).filter(Customer.group_id == group_id).all()
    
    # Get ALL available customers not already in this group
    # A customer can be in multiple groups, so we only exclude those already in THIS group
    available_customers = db.query(Customer).filter(
        Customer.group_id != group_id
    ).all()
    
    # Also include customers with no group assigned
    customers_no_group = db.query(Customer).filter(Customer.group_id == None).all()
    
    # Combine and deduplicate
    available_set = {c.id: c for c in available_customers}
    for c in customers_no_group:
        available_set[c.id] = c
    available_customers = list(available_set.values())
    
    # Get all groups organized by category for the customer modal
    all_groups = db.query(Group).all()
    
    return templates.TemplateResponse("group_detail.html", {
        "request": request,
        "categories": categories,
        "group": group,
        "customers": customers,
        "available_customers": available_customers,
        "all_groups": all_groups
    })


@router.get("/customers/{customer_id}", response_class=HTMLResponse)
async def customer_detail(customer_id: int, request: Request, db: Session = Depends(get_db)):
    """Customer detail page."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    categories = db.query(Category).all()
    subscriptions = db.query(Subscription).filter(Subscription.customer_id == customer_id).all()
    
    return templates.TemplateResponse("customer_detail.html", {
        "request": request,
        "categories": categories,
        "customer": customer,
        "subscriptions": subscriptions
    })


@router.get("/subscriptions/{subscription_id}", response_class=HTMLResponse)
async def subscription_detail(subscription_id: int, request: Request, db: Session = Depends(get_db)):
    """Subscription detail page."""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    categories = db.query(Category).all()
    
    return templates.TemplateResponse("subscription_detail.html", {
        "request": request,
        "categories": categories,
        "subscription": subscription
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    """Settings page."""
    categories = db.query(Category).all()
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "categories": categories
    })


@router.get("/links/render", response_class=HTMLResponse)
async def render_links(
    request: Request,
    source_type: str = None,
    source_id: int = None,
    target_type: str = None,
    target_id: int = None,
    db: Session = Depends(get_db)
):
    """Render links as HTML component."""
    query = db.query(Link)
    
    if source_type:
        query = query.filter(Link.source_type == source_type)
    if source_id:
        query = query.filter(Link.source_id == source_id)
    if target_type:
        query = query.filter(Link.target_type == target_type)
    if target_id:
        query = query.filter(Link.target_id == target_id)
    
    links = query.order_by(Link.confidence.desc()).all()
    
    return templates.TemplateResponse("components/related_links.html", {
        "request": request,
        "links": links
    })


@router.get("/links", response_class=HTMLResponse)
async def links_page(request: Request, db: Session = Depends(get_db)):
    """Dedicated links and relationships page."""
    categories = db.query(Category).all()
    all_links = db.query(Link).order_by(Link.confidence.desc()).all()
    
    total_links = len(all_links)
    accepted_links = len([l for l in all_links if l.user_decision == "accepted"])
    rejected_links = len([l for l in all_links if l.user_decision == "rejected"])
    pending_links = len([l for l in all_links if l.user_decision is None])
    
    return templates.TemplateResponse("links_page.html", {
        "request": request,
        "categories": categories,
        "links": all_links,
        "total_links": total_links,
        "accepted_links": accepted_links,
        "rejected_links": rejected_links,
        "pending_links": pending_links
    })


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, period: str = "30", db: Session = Depends(get_db)):
    """Analytics dashboard page."""
    # Parse period parameter
    today = date.today()
    if period == "all":
        start_date = None
    else:
        try:
            days = int(period)
            start_date = today - timedelta(days=days)
        except ValueError:
            start_date = today - timedelta(days=30)
    
    # Get all active subscriptions (optionally filtered by start_date)
    query = db.query(Subscription).filter(Subscription.status == "active")
    if start_date:
        query = query.filter(Subscription.start_date >= start_date)
    active_subs = query.all()
    
    # Also get all active subs for total counts
    all_active_subs = db.query(Subscription).filter(Subscription.status == "active").all()
    
    # Calculate totals
    total_spend = sum(s.cost for s in active_subs)
    active_count = len(active_subs)
    avg_cost = total_spend / active_count if active_count > 0 else 0
    
    # Get upcoming renewals (next 30 days)
    upcoming = [s for s in all_active_subs if s.next_renewal_date and (s.next_renewal_date - today).days <= 30 and (s.next_renewal_date - today).days >= 0]
    upcoming_renewals = len(upcoming)
    renewal_value = sum(s.cost for s in upcoming)
    
    # Category breakdown
    categories = db.query(Category).all()
    for cat in categories:
        cat_subs = [s for s in active_subs if s.category_id == cat.id]
        cat.total = sum(s.cost for s in cat_subs)
    
    # Top vendors
    from collections import defaultdict
    vendor_stats = defaultdict(lambda: {"count": 0, "total": 0})
    for sub in active_subs:
        vendor_stats[sub.vendor_name]["count"] += 1
        vendor_stats[sub.vendor_name]["total"] += sub.cost
    top_vendors = [{"name": k, "count": v["count"], "total": v["total"]} 
                   for k, v in sorted(vendor_stats.items(), key=lambda x: x[1]["total"], reverse=True)[:5]]
    
    # Billing cycles
    cycle_stats = defaultdict(int)
    for sub in active_subs:
        cycle_stats[sub.billing_cycle.value] += 1
    billing_cycles = [
        {"name": k.capitalize(), "count": v, "percentage": int(v/active_count*100) if active_count > 0 else 0,
         "icon": {"monthly": "📅", "yearly": "📆", "quarterly": "🗓️", "weekly": "📋"}.get(k, "📄")}
        for k, v in cycle_stats.items()
    ]
    
    # Status counts
    all_subs = db.query(Subscription).all()
    status_counts = {
        "active": len([s for s in all_subs if s.status.value == "active"]),
        "paused": len([s for s in all_subs if s.status.value == "paused"]),
        "cancelled": len([s for s in all_subs if s.status.value == "cancelled"])
    }
    
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "categories": categories,
        "total_spend": total_spend,
        "active_count": active_count,
        "avg_cost": avg_cost,
        "upcoming_renewals": upcoming_renewals,
        "renewal_value": renewal_value,
        "top_vendors": top_vendors,
        "billing_cycles": billing_cycles,
        "status_counts": status_counts
    })


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, db: Session = Depends(get_db)):
    """Reports and exports page."""
    from app.models.saved_report import SavedReport
    
    categories = db.query(Category).all()
    current_user = get_current_user(request, db)
    
    # Get saved reports for the current user
    if current_user:
        saved_reports = db.query(SavedReport).filter(
            SavedReport.user_id == current_user.id
        ).order_by(SavedReport.created_at.desc()).all()
    else:
        saved_reports = db.query(SavedReport).order_by(SavedReport.created_at.desc()).all()
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "categories": categories,
        "saved_reports": saved_reports,
        "current_user": current_user
    })


@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, db: Session = Depends(get_db)):
    """Users management page (admin only)."""
    current_user = get_current_user(request, db)
    
    if not current_user or not current_user.is_admin:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "message": "Access denied. Admin privileges required."
        }, status_code=403)
    
    categories = db.query(Category).all()
    users = db.query(User).order_by(User.id).all()
    
    return templates.TemplateResponse("users.html", {
        "request": request,
        "categories": categories,
        "users": users,
        "current_user": current_user
    })


# Integrations page removed - was non-functional


# AI dashboard removed - AI chat features have been disabled


@router.get("/partials/customer-options", response_class=HTMLResponse)
async def customer_options_partial(
    request: Request,
    category_id: int = None,
    selected_customer_id: int = None,
    db: Session = Depends(get_db)
):
    """Render customer options for dropdown - used in subscription modals."""
    query = db.query(Customer)
    
    # Filter by category if provided
    if category_id:
        query = query.filter(Customer.category_id == category_id)
    
    customers = query.order_by(Customer.name).all()
    
    # Build HTML options
    html = '<option value="">Select a customer</option>'
    
    if not customers:
        html += '<option value="" disabled>No customers in this category — create one first</option>'
    else:
        for customer in customers:
            selected = 'selected' if selected_customer_id and customer.id == selected_customer_id else ''
            html += f'<option value="{customer.id}" {selected}>{customer.name}</option>'
    
    return HTMLResponse(content=html)
