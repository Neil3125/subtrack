"""Email service for sending renewal notifications via MailerSend API."""
import httpx
import logging
from typing import Optional, Tuple
from datetime import date
import os

logger = logging.getLogger(__name__)

# MailerSend API endpoint
MAILERSEND_API_URL = "https://api.mailersend.com/v1/email"


class EmailService:
    """Service for sending email notifications via MailerSend API."""
    
    def __init__(self):
        """Initialize email service - config is loaded fresh each time."""
        pass
    
    def _get_config(self):
        """Get MailerSend configuration from environment (fresh read each time)."""
        return {
            "api_token": os.environ.get("MAILERSEND_API_TOKEN", ""),
            "from_email": os.environ.get("MAILERSEND_FROM_EMAIL", ""),
            "from_name": os.environ.get("MAILERSEND_FROM_NAME", "SubTrack Notifications")
        }
    
    @property
    def api_token(self):
        return self._get_config()["api_token"]
    
    @property
    def from_email(self):
        return self._get_config()["from_email"]
    
    @property
    def from_name(self):
        return self._get_config()["from_name"]
        
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        config = self._get_config()
        return bool(config["api_token"] and config["from_email"])
    
    def get_diagnostic_info(self) -> dict:
        """Get diagnostic information about email configuration (safe to expose)."""
        config = self._get_config()
        return {
            "configured": self.is_configured(),
            "provider": "MailerSend",
            "api_token_set": bool(config["api_token"]),
            "api_token_preview": config["api_token"][:10] + "***" if config["api_token"] else "(not set)",
            "from_email": config["from_email"] if config["from_email"] else "(not set)",
            "from_name": config["from_name"]
        }
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test MailerSend API connection by validating credentials."""
        if not self.is_configured():
            return False, "Email service not configured. Set MAILERSEND_API_TOKEN and MAILERSEND_FROM_EMAIL environment variables."
        
        config = self._get_config()
        try:
            # Test by checking account info via API
            logger.info("Testing MailerSend API connection...")
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    "https://api.mailersend.com/v1/api-quota",
                    headers={
                        "Authorization": f"Bearer {config['api_token']}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    logger.info("MailerSend API connection successful!")
                    return True, "MailerSend API connection successful"
                elif response.status_code == 401:
                    return False, "MailerSend API authentication failed - invalid API token"
                else:
                    return False, f"MailerSend API error: {response.status_code} - {response.text}"
                    
        except httpx.TimeoutException:
            error_msg = "Connection timeout - MailerSend API took too long to respond"
            logger.error(error_msg)
            return False, error_msg
        except httpx.RequestError as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Send an email via MailerSend API.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not to_email:
            return False, "No recipient email provided"
        
        if not self.is_configured():
            logger.warning("Email service not configured - MailerSend credentials missing")
            return False, "Email service not configured. Set MAILERSEND_API_TOKEN and MAILERSEND_FROM_EMAIL environment variables."
        
        config = self._get_config()
        logger.info(f"Attempting to send email to {to_email} via MailerSend")
        
        try:
            # Build the request payload
            payload = {
                "from": {
                    "email": config["from_email"],
                    "name": config["from_name"]
                },
                "to": [
                    {"email": to_email}
                ],
                "subject": subject,
                "html": body_html
            }
            
            # Add plain text version if provided
            if body_text:
                payload["text"] = body_text
            
            # Send via MailerSend API
            logger.info("Sending email via MailerSend API...")
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    MAILERSEND_API_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {config['api_token']}",
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    }
                )
                
                # MailerSend returns 202 Accepted on success
                if response.status_code == 202:
                    logger.info(f"Email sent successfully to {to_email}")
                    return True, "Email sent successfully"
                elif response.status_code == 401:
                    error_msg = "MailerSend API authentication failed - invalid API token"
                    logger.error(error_msg)
                    return False, error_msg
                elif response.status_code == 422:
                    # Validation error - parse the response for details
                    try:
                        error_data = response.json()
                        error_msg = f"Validation error: {error_data.get('message', response.text)}"
                    except:
                        error_msg = f"Validation error: {response.text}"
                    logger.error(error_msg)
                    return False, error_msg
                else:
                    error_msg = f"MailerSend API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return False, error_msg
                    
        except httpx.TimeoutException:
            error_msg = "Connection timeout - MailerSend API took too long to respond"
            logger.error(error_msg)
            return False, error_msg
        except httpx.RequestError as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def generate_renewal_notice_html(
        self,
        customer_name: str,
        subscription_vendor: str,
        subscription_plan: Optional[str],
        renewal_date: date,
        cost: float,
        currency: str,
        days_until_renewal: int
    ) -> str:
        """
        Generate HTML for a renewal notice email (for preview or sending).
        
        Returns:
            HTML string for the email body
        """
        # Format the renewal date
        renewal_date_str = renewal_date.strftime("%B %d, %Y")
        
        # Determine urgency
        if days_until_renewal <= 0:
            urgency = "OVERDUE"
            urgency_color = "#dc2626"
        elif days_until_renewal <= 7:
            urgency = "URGENT"
            urgency_color = "#ea580c"
        elif days_until_renewal <= 14:
            urgency = "SOON"
            urgency_color = "#f59e0b"
        else:
            urgency = "UPCOMING"
            urgency_color = "#10b981"
        
        plan_info = f" ({subscription_plan})" if subscription_plan else ""
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
                .urgency-badge {{ display: inline-block; background: {urgency_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e2e8f0; }}
                .detail-label {{ color: #64748b; }}
                .detail-value {{ font-weight: 600; }}
                .amount {{ font-size: 24px; color: #1e40af; font-weight: bold; }}
                .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; border-radius: 0 0 10px 10px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0 0 10px 0;">📋 Subscription Renewal Notice</h1>
                    <span class="urgency-badge">{urgency}</span>
                </div>
                <div class="content">
                    <p>Hello <strong>{customer_name}</strong>,</p>
                    <p>This is a reminder about your upcoming subscription renewal:</p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <div class="detail-row">
                            <span class="detail-label">Service</span>
                            <span class="detail-value">{subscription_vendor}{plan_info}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Renewal Date</span>
                            <span class="detail-value">{renewal_date_str}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Days Until Renewal</span>
                            <span class="detail-value">{days_until_renewal} days</span>
                        </div>
                        <div class="detail-row" style="border-bottom: none;">
                            <span class="detail-label">Amount</span>
                            <span class="amount">{currency} {cost:.2f}</span>
                        </div>
                    </div>
                    
                    <p>Please ensure your payment method is up to date to avoid any service interruption.</p>
                </div>
                <div class="footer">
                    <p>This email was sent by SubTrack - Subscription Management System</p>
                    <p>You received this because you are registered as the contact for this subscription.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def send_renewal_notice(
        self,
        customer_name: str,
        customer_email: str,
        subscription_vendor: str,
        subscription_plan: Optional[str],
        renewal_date: date,
        cost: float,
        currency: str,
        days_until_renewal: int
    ) -> Tuple[bool, str]:
        """
        Send a subscription renewal notice email.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not customer_email:
            return False, f"Customer '{customer_name}' has no email address"
        
        # Generate HTML body
        body_html = self.generate_renewal_notice_html(
            customer_name=customer_name,
            subscription_vendor=subscription_vendor,
            subscription_plan=subscription_plan,
            renewal_date=renewal_date,
            cost=cost,
            currency=currency,
            days_until_renewal=days_until_renewal
        )
        
        # Format the renewal date for subject
        renewal_date_str = renewal_date.strftime("%B %d, %Y")
        
        # Determine urgency for subject
        if days_until_renewal <= 0:
            urgency = "OVERDUE"
        elif days_until_renewal <= 7:
            urgency = "URGENT"
        elif days_until_renewal <= 14:
            urgency = "SOON"
        else:
            urgency = "UPCOMING"
        
        plan_info = f" ({subscription_plan})" if subscription_plan else ""
        subject = f"[{urgency}] Subscription Renewal: {subscription_vendor}{plan_info} - {renewal_date_str}"
        
        # Plain text version
        body_text = f"""
Subscription Renewal Notice - {urgency}

Hello {customer_name},

This is a reminder about your upcoming subscription renewal:

Service: {subscription_vendor}{plan_info}
Renewal Date: {renewal_date_str}
Days Until Renewal: {days_until_renewal} days
Amount: {currency} {cost:.2f}

Please ensure your payment method is up to date to avoid any service interruption.

---
This email was sent by SubTrack - Subscription Management System
        """
        
        return self.send_email(customer_email, subject, body_html, body_text)


# Singleton instance
email_service = EmailService()
