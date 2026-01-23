from app.services.email_service import email_service
import asyncio

async def test_send():
    print("Testing MailerSend Sending...")
    
    # Try sending to the sender address itself as a test
    recipient = "MS_6gokxf@acsinc.bb"
    print(f"Sending test email to {recipient}...")
    
    success, msg = email_service.send_email(
        to_email=recipient,
        subject="MailerSend Integration Test",
        body_html="<h1>Success!</h1><p>MailerSend API integration is working.</p>",
        body_text="Success! MailerSend API integration is working."
    )
    
    print(f"Success: {success}")
    print(f"Message: {msg}")

if __name__ == "__main__":
    asyncio.run(test_send())
