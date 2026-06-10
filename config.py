import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'unicracy-dev-secret-key-change-me')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/unicracy')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    
    # Email config
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    BREVO_FROM_EMAIL = os.getenv("BREVO_FROM_EMAIL")
    BREVO_FROM_NAME = os.getenv("BREVO_FROM_NAME", "Unicracy")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    MOCK_EMAIL = os.getenv("MOCK_EMAIL", "false").lower() == "true"
    BYPASS_OTP = os.getenv("BYPASS_OTP", "false").lower() == "true"
    
    # OTP config
    OTP_EXPIRY_SECONDS = int(os.getenv('OTP_EXPIRY_SECONDS', 300))
    
    # Google OAuth config
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')
    
    # Session config
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # App constants
    DEPARTMENTS = [
        'B.E. / B.Tech',
        'B.Sc.',
        'B.A.',
        'BCA',
        'MBA / PGDM',
        'B.Ed',
        'LL.M.',
        'B.A. LL.B.',
        'B.Pharma',
        'BBA',
        'UG Diploma',
        'M.A.',
        'B.Com',
        'LL.B.',
        'MCA',
        'PG Diploma',
        'Certificate',
        'M.E. / M.Tech',
        'M.Com',
        'B.Lib.I.Sc.',
        'Others',
    ]
    
    YEARS = ['1st Year', '2nd Year', '3rd Year', '4th Year']
