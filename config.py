import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'unicracy-dev-secret-key-change-me')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/unicracy')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    
    # Email config
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "true").lower() == "true"
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    
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
        'Computer Science',
        'Electronics & Communication',
        'Electrical & Electronics',
        'Mechanical Engineering',
        'Civil Engineering',
        'Information Technology',
        'Chemical Engineering',
        'Biotechnology',
    ]
    
    YEARS = ['1st Year', '2nd Year', '3rd Year', '4th Year']
