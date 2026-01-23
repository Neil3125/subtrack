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
            "api_key": os.environ.get("MAILERSEND_API_KEY"),
            "from_email": os.environ.get("MAILERSEND_FROM_EMAIL"),
            "from_name": os.environ.get("MAILERSEND_FROM_NAME", "SubTrack Notifications")
        }
    
    @property
    def api_key(self):
        return self._get_config()["api_key"]
    
    @property
    def from_email(self):
        return self._get_config()["from_email"]
    
    @property
    def from_name(self):
        return self._get_config()["from_name"]
        
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        config = self._get_config()
        return bool(config["api_key"])
    
    def get_diagnostic_info(self) -> dict:
        """Get diagnostic information about email configuration (safe to expose)."""
        config = self._get_config()
        return {
            "configured": self.is_configured(),
            "provider": "MailerSend",
            "api_key_set": bool(config["api_key"]),
            "api_key_preview": config["api_key"][:12] + "***" if config["api_key"] else "(not set)",
            "from_email": config["from_email"] if config["from_email"] else "(not set)",
            "from_name": config["from_name"]
        }
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test MailerSend API connection by validating credentials."""
        if not self.is_configured():
            return False, "Email service not configured. Set MAILERSEND_API_KEY environment variable."
        
        config = self._get_config()
        try:
            # Test by checking domains endpoint
            logger.info("Testing MailerSend API connection...")
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    "https://api.mailersend.com/v1/domains",
                    headers={
                        "Authorization": f"Bearer {config['api_key']}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    logger.info("MailerSend API connection successful!")
                    return True, "MailerSend API connection successful"
                elif response.status_code == 403:
                    # 403 Forbidden often means the key is valid but has restricted permissions (e.g. can't list domains)
                    # For a send-only key, this implies connection is likely fine
                    logger.info("MailerSend API reachable (403 Forbidden - likely restricted permissions key)")
                    return True, "MailerSend API reachable (restricted permissions)"
                elif response.status_code == 401:
                    return False, "MailerSend API authentication failed - invalid API key"
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
            logger.warning("Email service not configured - MailerSend API key missing")
            return False, "Email service not configured. Set MAILERSEND_API_KEY environment variable."
        
        config = self._get_config()
        logger.info(f"Attempting to send email to {to_email} via MailerSend")
        
        try:
            # Build the request payload for MailerSend
            # https://developers.mailersend.com/api/v1/email.html#send-an-email
            payload = {
                "from": {
                    "email": config['from_email'],
                    "name": config['from_name']
                },
                "to": [
                    {
                        "email": to_email
                    }
                ],
                "subject": subject,
                "html": body_html,
                "text": body_text or "Please view this email in a client that supports HTML."
            }
            
            # Send via MailerSend API
            logger.info("Sending email via MailerSend API...")
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    MAILERSEND_API_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {config['api_key']}",
                        "Content-Type": "application/json"
                    }
                )
                
                # MailerSend returns 202 Accepted on success
                if response.status_code == 202:
                    # Capture the X-Message-Id header if present
                    message_id = response.headers.get("X-Message-Id", "queued")
                    logger.info(f"Email queued successfully for {to_email} (ID: {message_id})")
                    return True, f"Email accepted for delivery (ID: {message_id})"
                elif response.status_code == 401:
                    error_msg = "MailerSend API authentication failed - invalid API key"
                    logger.error(error_msg)
                    return False, error_msg
                elif response.status_code == 422:
                    # Validation error
                    try:
                        error_data = response.json()
                        error_msg = f"Validation error: {error_data.get('message', response.text)}"
                        if 'errors' in error_data:
                            error_msg += f" Details: {error_data['errors']}"
                    except:
                        error_msg = f"Validation error: {response.text}"
                    logger.error(error_msg)
                    return False, error_msg
                elif response.status_code == 429:
                    error_msg = "Rate limit exceeded - too many emails sent."
                    logger.error(error_msg)
                    return False, error_msg
                else:
                    try:
                        error_data = response.json()
                        error_msg = f"MailerSend API error: {error_data.get('message', response.text)}"
                    except:
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
        
        # Determine urgency messaging
        if days_until_renewal <= 0:
            urgency = "OVERDUE"
            urgency_color = "#dc2626"
            urgency_bg = "#fef2f2"
            urgency_message = f"This subscription renewal is <strong>{abs(days_until_renewal)} days overdue</strong>. Please take action immediately to avoid service interruption."
        elif days_until_renewal <= 7:
            urgency = "DUE SOON"
            urgency_color = "#ea580c"
            urgency_bg = "#fff7ed"
            urgency_message = f"Your subscription renews in <strong>{days_until_renewal} days</strong>. Please ensure your payment details are up to date."
        elif days_until_renewal <= 14:
            urgency = "UPCOMING"
            urgency_color = "#f59e0b"
            urgency_bg = "#fffbeb"
            urgency_message = f"Your subscription renews in <strong>{days_until_renewal} days</strong>. This is a friendly reminder to review your subscription."
        else:
            urgency = "REMINDER"
            urgency_color = "#10b981"
            urgency_bg = "#f0fdf4"
            urgency_message = f"Your subscription renews in <strong>{days_until_renewal} days</strong>. No action is required at this time."
        
        plan_display = f"{subscription_vendor} - {subscription_plan}" if subscription_plan else subscription_vendor
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscription Renewal Notice</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6; line-height: 1.6;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f3f4f6;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 0 auto; max-width: 600px;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 40px 30px; border-radius: 12px 12px 0 0; text-align: center;">
                            <h1 style="margin: 0 0 15px 0; color: #ffffff; font-size: 28px; font-weight: 600;">
                                Subscription Renewal Notice
                            </h1>
                            <span style="display: inline-block; background: {urgency_color}; color: #ffffff; padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; letter-spacing: 0.5px;">
                                {urgency}
                            </span>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="background-color: #ffffff; padding: 40px;">
                            
                            <!-- Greeting -->
                            <p style="margin: 0 0 25px 0; color: #374151; font-size: 16px;">
                                Hi <strong>{customer_name}</strong>,
                            </p>
                            
                            <!-- Urgency Message Box -->
                            <div style="background-color: {urgency_bg}; border-left: 4px solid {urgency_color}; padding: 16px 20px; margin-bottom: 30px; border-radius: 0 8px 8px 0;">
                                <p style="margin: 0; color: #374151; font-size: 15px;">
                                    {urgency_message}
                                </p>
                            </div>
                            
                            <!-- Subscription Details Card -->
                            <div style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px; padding: 25px; margin-bottom: 30px;">
                                <h2 style="margin: 0 0 20px 0; color: #111827; font-size: 18px; font-weight: 600;">
                                    Subscription Details
                                </h2>
                                
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                    <tr>
                                        <td style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                                            <span style="color: #6b7280; font-size: 14px;">Service</span>
                                        </td>
                                        <td style="padding: 12px 0; border-bottom: 1px solid #e5e7eb; text-align: right;">
                                            <span style="color: #111827; font-size: 14px; font-weight: 600;">{plan_display}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                                            <span style="color: #6b7280; font-size: 14px;">Renewal Date</span>
                                        </td>
                                        <td style="padding: 12px 0; border-bottom: 1px solid #e5e7eb; text-align: right;">
                                            <span style="color: #111827; font-size: 14px; font-weight: 600;">{renewal_date_str}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 16px 0 0 0;">
                                            <span style="color: #6b7280; font-size: 14px;">Amount Due</span>
                                        </td>
                                        <td style="padding: 16px 0 0 0; text-align: right;">
                                            <span style="color: #667eea; font-size: 24px; font-weight: 700;">{currency} {cost:.2f}</span>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Help Text -->
                            <p style="margin: 0; color: #6b7280; font-size: 14px;">
                                If you have any questions about this renewal or need to make changes to your subscription, please contact your account manager.
                            </p>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #1f2937; padding: 30px 40px; border-radius: 0 0 12px 12px; text-align: center;">
                            <p style="margin: 0 0 10px 0; color: #9ca3af; font-size: 13px;">
                                This is an automated message from SubTrack
                            </p>
                            <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                You received this email because you are the registered contact for this subscription.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
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
        plan_display = f"{subscription_vendor} - {subscription_plan}" if subscription_plan else subscription_vendor
        
        if days_until_renewal <= 0:
            urgency_text = f"This subscription renewal is {abs(days_until_renewal)} days overdue. Please take action immediately."
        elif days_until_renewal <= 7:
            urgency_text = f"Your subscription renews in {days_until_renewal} days. Please ensure your payment details are up to date."
        elif days_until_renewal <= 14:
            urgency_text = f"Your subscription renews in {days_until_renewal} days. This is a friendly reminder to review your subscription."
        else:
            urgency_text = f"Your subscription renews in {days_until_renewal} days. No action is required at this time."
        
        body_text = f"""
SUBSCRIPTION RENEWAL NOTICE

Hi {customer_name},

{urgency_text}

SUBSCRIPTION DETAILS
--------------------
Service:      {plan_display}
Renewal Date: {renewal_date_str}
Amount Due:   {currency} {cost:.2f}

If you have any questions about this renewal or need to make changes to your subscription, please contact your account manager.

---
This is an automated message from SubTrack.
You received this email because you are the registered contact for this subscription.
        """
        
        return self.send_email(customer_email, subject, body_html, body_text)


# Singleton instance
email_service = EmailService()
