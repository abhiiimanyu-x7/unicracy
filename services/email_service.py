import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        
    if not Config.EMAIL_USER or not Config.EMAIL_PASS:
        print("Warning: Email credentials not configured. OTP not sent.")
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

    msg = MIMEMultipart()
    msg['From'] = Config.EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        if Config.EMAIL_USE_SSL:
            server = smtplib.SMTP_SSL(
                Config.EMAIL_HOST,
                int(Config.EMAIL_PORT),
                timeout=10
            )
        else:
            server = smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT)
            server.starttls()
            
        server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
        server.send_message(msg)
        
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
