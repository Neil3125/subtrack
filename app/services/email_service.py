"""Email service for sending renewal notifications."""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple
from datetime import date
import os

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        """Initialize email service with environment configuration."""
        self.smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")
        self.from_email = os.environ.get("SMTP_FROM_EMAIL", self.smtp_user)
        self.from_name = os.environ.get("SMTP_FROM_NAME", "SubTrack Notifications")
        
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.smtp_user and self.smtp_password)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Send an email.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not to_email:
            return False, "No recipient email provided"
        
        if not self.is_configured():
            logger.warning("Email service not configured - SMTP credentials missing")
            return False, "Email service not configured. Set SMTP_USER and SMTP_PASSWORD environment variables."
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            # Add text and HTML parts
            if body_text:
                part1 = MIMEText(body_text, "plain")
                msg.attach(part1)
            
            part2 = MIMEText(body_html, "html")
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False, "Email authentication failed. Check SMTP credentials."
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False, f"Failed to send email: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False, f"Unexpected error: {str(e)}"
    
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
        
        subject = f"[{urgency}] Subscription Renewal: {subscription_vendor}{plan_info} - {renewal_date_str}"
        
        body_html = f"""
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
