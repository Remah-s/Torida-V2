"""
TORIDA Database Setup
=====================
SQLAlchemy database instance initialization.
"""
from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the Flask app.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        # Import all models to ensure they are registered
        from app.models import (
            Governorate, UserType, Role, Permission, RolePermission,
            CodeSequence, User, UserRole, BusinessProfile, OTP,
            Address, Category, ProductSequence, Product, ProductImage,
            Order, OrderItem, OrderStatusHistory, Payment,
            ProductReview, Cart, CartItem, Wishlist, Notification
        )
        
        # Create all tables (if not exists)
        # Note: In production, use migrations (Flask-Migrate/Alembic)
        db.create_all()


def reset_db():
    """
    Drop and recreate all tables.
    WARNING: This will delete all data!
    """
    db.drop_all()
    db.create_all()
