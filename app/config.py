"""
TORIDA Backend Configuration
============================
Configuration settings for the Flask application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PUBLIC_API_BASE_URL = os.getenv('PUBLIC_API_BASE_URL', '').rstrip('/')

    _cors_origins = os.getenv('CORS_ORIGINS', '*').strip()
    if _cors_origins == '*':
        CORS_ORIGINS = '*'
    elif _cors_origins:
        CORS_ORIGINS = [origin.strip() for origin in _cors_origins.split(',') if origin.strip()]
    else:
        CORS_ORIGINS = ['*']  # Default to allow all origins
    
    # Database Configuration
    MYSQL_HOST = os.getenv('MYSQLHOST', os.getenv('DB_HOST', 'localhost'))
    MYSQL_PORT = int(os.getenv('MYSQLPORT', os.getenv('DB_PORT', 3306)))
    MYSQL_USER = os.getenv('MYSQLUSER', os.getenv('DB_USER', 'root'))
    MYSQL_PASSWORD = os.getenv('MYSQLPASSWORD', os.getenv('DB_PASSWORD', 'Ramahr132687r'))
    MYSQL_DB = os.getenv('MYSQLDATABASE', os.getenv('DB_NAME', 'torida'))
    
    # SQLAlchemy Settings
    _db_url = os.getenv('MYSQL_URL')
    if _db_url:
        if _db_url.startswith("mysql://"):
            _db_url = _db_url.replace("mysql://", "mysql+mysqlconnector://", 1)
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@"
            f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Optimize connection pool for serverless environments (Vercel)
    # Use smaller pool size and recycle connections more frequently
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_recycle': 1800,  # Recycle connections every 30 minutes
        'pool_pre_ping': True,  # Test connections before using them
    }
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days
    JWT_ALGORITHM = 'HS256'
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'Torida <noreply@torida.com>')
    
    # OTP Settings
    OTP_LENGTH = int(os.getenv('OTP_LENGTH', 6))
    OTP_EXPIRY_MINUTES = int(os.getenv('OTP_EXPIRY_MINUTES', 10))
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')  # Use /tmp for serverless
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,webp').split(',')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
