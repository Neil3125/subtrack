"""Subscription schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from app.models.subscription import SubscriptionStatus, BillingCycle


class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    vendor_name: str = Field(..., min_length=1, max_length=200)
    plan_name: Optional[str] = None
    cost: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    billing_cycle: BillingCycle
    custom_billing_amount: Optional[int] = None
    custom_billing_unit: Optional[str] = None
    start_date: date
    next_renewal_date: date
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    country: Optional[str] = None
    notes: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a subscription."""
    customer_id: int
    # Primary category (backward compatibility). Optional if category_ids provided.
    category_id: Optional[int] = None
    # Multi-select categories
    category_ids: Optional[List[int]] = None
    # Flag to save as smart template
    save_template: bool = False


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription."""
    vendor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    plan_name: Optional[str] = None
    cost: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    billing_cycle: Optional[BillingCycle] = None
    custom_billing_amount: Optional[int] = None
    custom_billing_unit: Optional[str] = None
    start_date: Optional[date] = None
    next_renewal_date: Optional[date] = None
    status: Optional[SubscriptionStatus] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    customer_id: Optional[int] = None
    # Primary category (backward compatibility)
    category_id: Optional[int] = None
    # Multi-select categories
    category_ids: Optional[List[int]] = None


class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription response."""
    id: int
    customer_id: int
    category_id: int
    category_ids: List[int] = []
    
    class Config:
        from_attributes = True
