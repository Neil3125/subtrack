"""Search API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Dict, Any
from app.database import get_db
from app.models import Category, Group, Customer, Subscription

router = APIRouter()


@router.get("")
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Global search across all entities."""
    search_term = f"%{q.lower()}%"
    
    # Search categories
    categories = db.query(Category).filter(
        or_(
            func.lower(Category.name).like(search_term),
            func.lower(Category.description).like(search_term)
        )
    ).limit(10).all()
    
    # Search groups
    groups = db.query(Group).filter(
        or_(
            func.lower(Group.name).like(search_term),
            func.lower(Group.notes).like(search_term)
        )
    ).limit(10).all()
    
    # Search customers
    customers = db.query(Customer).filter(
        or_(
            func.lower(Customer.name).like(search_term),
            func.lower(Customer.email).like(search_term),
            func.lower(Customer.tags).like(search_term),
            func.lower(Customer.notes).like(search_term)
        )
    ).limit(10).all()
    
    # Search subscriptions
    subscriptions = db.query(Subscription).filter(
        or_(
            func.lower(Subscription.vendor_name).like(search_term),
            func.lower(Subscription.plan_name).like(search_term),
            func.lower(Subscription.notes).like(search_term)
        )
    ).limit(10).all()
    
    return {
        'query': q,
        'results': {
            'categories': [
                {'id': c.id, 'name': c.name, 'type': 'category'}
                for c in categories
            ],
            'groups': [
                {'id': g.id, 'name': g.name, 'category_id': g.category_id, 'type': 'group'}
                for g in groups
            ],
            'customers': [
                {'id': c.id, 'name': c.name, 'category_id': c.category_id, 'type': 'customer'}
                for c in customers
            ],
            'subscriptions': [
                {
                    'id': s.id, 
                    'vendor': s.vendor_name, 
                    'plan': s.plan_name,
                    'customer_id': s.customer_id,
                    'type': 'subscription'
                }
                for s in subscriptions
            ]
        },
        'total_results': len(categories) + len(groups) + len(customers) + len(subscriptions)
    }
