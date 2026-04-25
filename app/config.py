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
    
    # Database Configuration
    MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('DB_PORT', 3306))
    MYSQL_USER = os.getenv('DB_USER', 'root')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', 'Ramahr132687r')
    MYSQL_DB = os.getenv('DB_NAME', 'torida')
    
    # SQLAlchemy Settings
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
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
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
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


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
