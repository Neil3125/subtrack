from pydantic import BaseModel
from typing import Optional
from app.models.subscription import BillingCycle

class SubscriptionTemplateBase(BaseModel):
    name: str
    vendor_name: Optional[str] = None
    plan_name: Optional[str] = None
    cost: Optional[float] = None
    currency: Optional[str] = "USD"
    billing_cycle: Optional[BillingCycle] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None

class SubscriptionTemplateCreate(SubscriptionTemplateBase):
    pass

class SubscriptionTemplateUpdate(SubscriptionTemplateBase):
    name: Optional[str] = None

class SubscriptionTemplateResponse(SubscriptionTemplateBase):
    id: int
    
    class Config:
        from_attributes = True
