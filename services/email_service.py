import random
import string
import requests
from config import Config

def generate_otp(length=6):
    """Generate a random numeric OTP of specified length."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(to_email, otp):
    """Send an OTP email to the given address."""
    if Config.MOCK_EMAIL:
        print("\n" + "="*50)
        print(f" MOCK EMAIL: Sent OTP [{otp}] to {to_email} ")
        print("="*50 + "\n")
        return True
        
    if not Config.RESEND_API_KEY:
        print("Warning: RESEND_API_KEY not configured. OTP not sent.")
        return False
        
    subject = "Your UNICRACY Registration OTP"
    body = f"""
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #4a6fa5;">UNICRACY - Campus Elections</h2>
                <p>Hello,</p>
                <p>You have requested to register for the UNICRACY election platform. Please use the following One-Time Password (OTP) to complete your registration:</p>
                <div style="background-color: #f4f4f4; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <h1 style="margin: 0; letter-spacing: 5px; color: #333;">{otp}</h1>
                </div>
                <p>This OTP is valid for {Config.OTP_EXPIRY_SECONDS // 60} minutes.</p>
                <p>If you did not request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>The UNICRACY Team</p>
            </div>
        </body>
    </html>
    """

    headers = {
        "Authorization": f"Bearer {Config.RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": Config.RESEND_FROM_EMAIL,
        "to": to_email,
        "subject": subject,
        "html": body
    }

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers=headers,
            timeout=10
        )
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Resend API error (status {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"Error sending email via Resend API: {e}")
        return False
