"""Email notification API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from app.database import get_db
from app.models import Subscription, Customer
from app.models.renewal_notice import RenewalNotice
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config")
def get_email_config():
    """Get email configuration status (without exposing credentials)."""
    return {
        "configured": email_service.is_configured(),
        "smtp_host": email_service.smtp_host,
        "smtp_port": email_service.smtp_port,
        "from_email": email_service.from_email if email_service.is_configured() else None,
        "message": "Email service is configured and ready" if email_service.is_configured() 
                   else "Email service not configured. Set SMTP_USER and SMTP_PASSWORD environment variables."
    }


@router.post("/test")
def send_test_email(to_email: str, db: Session = Depends(get_db)):
    """Send a test email to verify configuration."""
    if not email_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Email service not configured. Set SMTP_USER, SMTP_PASSWORD environment variables."
        )
    
    subject = "SubTrack Test Email"
    body_html = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>🎉 Test Email Successful!</h2>
        <p>Your SubTrack email configuration is working correctly.</p>
        <p>You can now send renewal notices to your customers.</p>
        <hr>
        <p style="color: #666; font-size: 12px;">Sent from SubTrack Subscription Manager</p>
    </body>
    </html>
    """
    body_text = "Test Email Successful! Your SubTrack email configuration is working correctly."
    
    success, message = email_service.send_email(to_email, subject, body_html, body_text)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=500, detail=message)


@router.post("/renewal-notice/{subscription_id}")
def send_renewal_notice(
    subscription_id: int,
    override_email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Send a renewal notice email for a specific subscription.
    
    Args:
        subscription_id: ID of the subscription
        override_email: Optional email to send to instead of customer's email
    """
    # Get subscription with customer
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    customer = subscription.customer
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found for this subscription")
    
    # Determine recipient email
    recipient_email = override_email or customer.email
    
    if not recipient_email:
        raise HTTPException(
            status_code=400,
            detail=f"Customer '{customer.name}' has no email address. Provide override_email parameter."
        )
    
    # Check if email service is configured
    if not email_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Email service not configured. Set SMTP_USER, SMTP_PASSWORD environment variables."
        )
    
    # Send the email
    success, message = email_service.send_renewal_notice(
        customer_name=customer.name,
        customer_email=recipient_email,
        subscription_vendor=subscription.vendor_name,
        subscription_plan=subscription.plan_name,
        renewal_date=subscription.next_renewal_date,
        cost=subscription.cost,
        currency=subscription.currency,
        days_until_renewal=subscription.days_until_renewal()
    )
    
    # Record the notice attempt
    notice = RenewalNotice(
        subscription_id=subscription.id,
        customer_id=customer.id,
        recipient_email=recipient_email,
        subject=f"Renewal Notice: {subscription.vendor_name}",
        success=success,
        error_message=None if success else message,
        notice_type="manual",
        renewal_date_at_send=datetime.combine(subscription.next_renewal_date, datetime.min.time())
    )
    db.add(notice)
    db.commit()
    
    if success:
        logger.info(f"Renewal notice sent for subscription {subscription_id} to {recipient_email}")
        return {
            "success": True,
            "message": message,
            "subscription_id": subscription_id,
            "recipient": recipient_email,
            "vendor": subscription.vendor_name
        }
    else:
        logger.error(f"Failed to send renewal notice for subscription {subscription_id}: {message}")
        raise HTTPException(status_code=500, detail=message)


@router.get("/renewal-notices")
def get_renewal_notices(
    subscription_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get history of sent renewal notices."""
    query = db.query(RenewalNotice)
    
    if subscription_id:
        query = query.filter(RenewalNotice.subscription_id == subscription_id)
    if customer_id:
        query = query.filter(RenewalNotice.customer_id == customer_id)
    
    notices = query.order_by(RenewalNotice.sent_at.desc()).limit(limit).all()
    
    return [
        {
            "id": n.id,
            "subscription_id": n.subscription_id,
            "customer_id": n.customer_id,
            "recipient_email": n.recipient_email,
            "subject": n.subject,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
            "success": n.success,
            "error_message": n.error_message,
            "notice_type": n.notice_type
        }
        for n in notices
    ]


@router.get("/upcoming-renewals")
def get_upcoming_renewals(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get subscriptions with upcoming renewals that may need notices.
    
    Returns subscriptions renewing within the specified days, along with
    information about whether notices have been sent.
    """
    today = date.today()
    end_date = today + timedelta(days=days)
    
    # Get active subscriptions renewing soon
    subscriptions = db.query(Subscription).filter(
        Subscription.status == "active",
        Subscription.next_renewal_date >= today,
        Subscription.next_renewal_date <= end_date
    ).order_by(Subscription.next_renewal_date).all()
    
    results = []
    for sub in subscriptions:
        # Check if notice was already sent for this renewal period
        recent_notice = db.query(RenewalNotice).filter(
            RenewalNotice.subscription_id == sub.id,
            RenewalNotice.success == True,
            RenewalNotice.sent_at >= datetime.now() - timedelta(days=7)  # Within last 7 days
        ).first()
        
        customer = sub.customer
        results.append({
            "subscription_id": sub.id,
            "vendor_name": sub.vendor_name,
            "plan_name": sub.plan_name,
            "cost": sub.cost,
            "currency": sub.currency,
            "next_renewal_date": sub.next_renewal_date.isoformat(),
            "days_until_renewal": sub.days_until_renewal(),
            "customer_id": customer.id if customer else None,
            "customer_name": customer.name if customer else "Unknown",
            "customer_email": customer.email if customer else None,
            "has_email": bool(customer and customer.email),
            "notice_sent_recently": bool(recent_notice),
            "last_notice_date": recent_notice.sent_at.isoformat() if recent_notice else None
        })
    
    return {
        "total": len(results),
        "with_email": sum(1 for r in results if r["has_email"]),
        "without_email": sum(1 for r in results if not r["has_email"]),
        "already_notified": sum(1 for r in results if r["notice_sent_recently"]),
        "subscriptions": results
    }


@router.post("/send-batch-notices")
def send_batch_renewal_notices(
    days_threshold: int = 14,
    dry_run: bool = True,
    db: Session = Depends(get_db)
):
    """
    Send renewal notices to all customers with subscriptions renewing soon.
    
    Args:
        days_threshold: Send notices for subscriptions renewing within this many days
        dry_run: If True, just return what would be sent without actually sending
    
    This endpoint:
    - Finds active subscriptions renewing within the threshold
    - Skips subscriptions that already received a notice in the last 7 days
    - Skips customers without email addresses (logged for reporting)
    - Records all sent notices to prevent duplicates
    """
    if not email_service.is_configured() and not dry_run:
        raise HTTPException(
            status_code=503,
            detail="Email service not configured. Set SMTP_USER, SMTP_PASSWORD environment variables."
        )
    
    today = date.today()
    end_date = today + timedelta(days=days_threshold)
    
    # Get active subscriptions renewing soon
    subscriptions = db.query(Subscription).filter(
        Subscription.status == "active",
        Subscription.next_renewal_date >= today,
        Subscription.next_renewal_date <= end_date
    ).order_by(Subscription.next_renewal_date).all()
    
    results = {
        "sent": [],
        "skipped_no_email": [],
        "skipped_already_notified": [],
        "failed": [],
        "dry_run": dry_run
    }
    
    for sub in subscriptions:
        customer = sub.customer
        
        # Skip if no customer
        if not customer:
            results["skipped_no_email"].append({
                "subscription_id": sub.id,
                "vendor": sub.vendor_name,
                "reason": "No customer associated"
            })
            continue
        
        # Skip if no email
        if not customer.email:
            results["skipped_no_email"].append({
                "subscription_id": sub.id,
                "vendor": sub.vendor_name,
                "customer": customer.name,
                "reason": "Customer has no email address"
            })
            continue
        
        # Check if already notified recently
        recent_notice = db.query(RenewalNotice).filter(
            RenewalNotice.subscription_id == sub.id,
            RenewalNotice.success == True,
            RenewalNotice.sent_at >= datetime.now() - timedelta(days=7)
        ).first()
        
        if recent_notice:
            results["skipped_already_notified"].append({
                "subscription_id": sub.id,
                "vendor": sub.vendor_name,
                "customer": customer.name,
                "last_notice": recent_notice.sent_at.isoformat()
            })
            continue
        
        # Send or simulate
        if dry_run:
            results["sent"].append({
                "subscription_id": sub.id,
                "vendor": sub.vendor_name,
                "customer": customer.name,
                "email": customer.email,
                "days_until_renewal": sub.days_until_renewal(),
                "status": "would_send"
            })
        else:
            # Actually send the email
            success, message = email_service.send_renewal_notice(
                customer_name=customer.name,
                customer_email=customer.email,
                subscription_vendor=sub.vendor_name,
                subscription_plan=sub.plan_name,
                renewal_date=sub.next_renewal_date,
                cost=sub.cost,
                currency=sub.currency,
                days_until_renewal=sub.days_until_renewal()
            )
            
            # Record the notice
            notice = RenewalNotice(
                subscription_id=sub.id,
                customer_id=customer.id,
                recipient_email=customer.email,
                subject=f"Renewal Notice: {sub.vendor_name}",
                success=success,
                error_message=None if success else message,
                notice_type=f"{days_threshold}_day_batch",
                renewal_date_at_send=datetime.combine(sub.next_renewal_date, datetime.min.time())
            )
            db.add(notice)
            
            if success:
                results["sent"].append({
                    "subscription_id": sub.id,
                    "vendor": sub.vendor_name,
                    "customer": customer.name,
                    "email": customer.email,
                    "status": "sent"
                })
            else:
                results["failed"].append({
                    "subscription_id": sub.id,
                    "vendor": sub.vendor_name,
                    "customer": customer.name,
                    "email": customer.email,
                    "error": message
                })
    
    if not dry_run:
        db.commit()
    
    # Summary
    results["summary"] = {
        "total_checked": len(subscriptions),
        "sent_count": len(results["sent"]),
        "skipped_no_email_count": len(results["skipped_no_email"]),
        "skipped_already_notified_count": len(results["skipped_already_notified"]),
        "failed_count": len(results["failed"])
    }
    
    return results
