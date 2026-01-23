from app.services.email_service import email_service
import asyncio

async def test_email():
    print("Testing MailerSend Configuration...")
    print(f"Configured: {email_service.is_configured()}")
    print(f"Provider: {email_service.get_diagnostic_info()['provider']}")
    print(f"API Key Preview: {email_service.get_diagnostic_info()['api_key_preview']}")
    
    print("\nTesting Connection...")
    success, msg = email_service.test_connection()
    print(f"Success: {success}")
    print(f"Message: {msg}")

if __name__ == "__main__":
    asyncio.run(test_email())
