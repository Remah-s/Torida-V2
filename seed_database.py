#!/usr/bin/env python
"""
Seed Database with Test Data
=============================
Populate the TORIDA database with test data for Postman testing.
Run this after initializing the database schema.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import (
    User, UserType, Governorate, Address, Category, Product, ProductImage,
    Cart, CartItem, Order, OrderItem, OrderStatusHistory, Payment,
    Role, Permission, UserRole, RolePermission, Notification, ProductReview,
    Wishlist, OTP
)
from app.utils.auth import hash_password
from app.utils.helpers import generate_otp


def create_app_context():
    """Create app context for database operations"""
    app = create_app()
    return app


def seed_user_types(db):
    """Seed user types"""
    user_types = [
        UserType(name="Supplier", description="Wholesale supplier"),
        UserType(name="Retailer", description="Retail business"),
        UserType(name="Company", description="Large company"),
    ]
    
    for ut in user_types:
        if not UserType.query.filter_by(name=ut.name).first():
            db.session.add(ut)
    
    db.session.commit()
    print("✓ User types seeded")


def seed_governorates(db):
    """Seed Egyptian governorates"""
    governorates = [
        Governorate(name="Cairo", code="CA"),
        Governorate(name="Giza", code="GZ"),
        Governorate(name="Alexandria", code="AX"),
        Governorate(name="Dakahlia", code="DK"),
        Governorate(name="Red Sea", code="RS"),
        Governorate(name="Beheira", code="BH"),
        Governorate(name="Fayoum", code="FY"),
        Governorate(name="Gharbia", code="GH"),
        Governorate(name="Assiut", code="AS"),
        Governorate(name="Suez", code="SZ"),
        Governorate(name="Ismailia", code="IS"),
        Governorate(name="Minya", code="MY"),
        Governorate(name="Luxor", code="LX"),
        Governorate(name="Aswan", code="AW"),
    ]
    
    for gov in governorates:
        if not Governorate.query.filter_by(name=gov.name).first():
            db.session.add(gov)
    
    db.session.commit()
    print("✓ Governorates seeded")


def seed_test_users(db):
    """Seed test users"""
    from app.utils.auth import hash_password
    
    users_data = [
        {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "01012345678",
            "password": "Password123!",
            "type_id": 1,
            "gov_id": 1,
        },
        {
            "full_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "01087654321",
            "password": "Password123!",
            "type_id": 2,
            "gov_id": 2,
        },
        {
            "full_name": "Admin User",
            "email": "admin@example.com",
            "phone": "01011111111",
            "password": "AdminPass123!",
            "type_id": 3,
            "gov_id": 1,
        },
    ]
    
    for user_data in users_data:
        existing = User.query.filter_by(email=user_data["email"]).first()
        if not existing:
            user = User(
                full_name=user_data["full_name"],
                email=user_data["email"],
                phone=user_data["phone"],
                password_hash=hash_password(user_data["password"]),
                type_id=user_data["type_id"],
                gov_id=user_data["gov_id"],
                is_active=True,
                is_email_verified=True,
            )
            db.session.add(user)
    
    db.session.commit()
    print("✓ Test users seeded")


def seed_roles(db):
    """Seed roles"""
    roles_data = [
        {"name": "Admin", "description": "Administrator role"},
        {"name": "Manager", "description": "Manager role"},
        {"name": "User", "description": "Regular user role"},
        {"name": "Guest", "description": "Guest user role"},
    ]
    
    for role_data in roles_data:
        existing = Role.query.filter_by(name=role_data["name"]).first()
        if not existing:
            role = Role(**role_data)
            db.session.add(role)
    
    db.session.commit()
    print("✓ Roles seeded")


def seed_permissions(db):
    """Seed permissions"""
    permissions_data = [
        {"name": "view_users", "description": "Can view users"},
        {"name": "create_user", "description": "Can create users"},
        {"name": "edit_user", "description": "Can edit users"},
        {"name": "delete_user", "description": "Can delete users"},
        {"name": "view_products", "description": "Can view products"},
        {"name": "create_product", "description": "Can create products"},
        {"name": "edit_product", "description": "Can edit products"},
        {"name": "delete_product", "description": "Can delete products"},
        {"name": "view_orders", "description": "Can view orders"},
        {"name": "create_order", "description": "Can create orders"},
        {"name": "edit_order", "description": "Can edit orders"},
        {"name": "delete_order", "description": "Can delete orders"},
    ]
    
    for perm_data in permissions_data:
        existing = Permission.query.filter_by(name=perm_data["name"]).first()
        if not existing:
            perm = Permission(**perm_data)
            db.session.add(perm)
    
    db.session.commit()
    print("✓ Permissions seeded")


def seed_categories(db):
    """Seed product categories"""
    categories_data = [
        {"name": "Electronics", "description": "Electronic devices and accessories"},
        {"name": "Clothing", "description": "Apparel and fashion items"},
        {"name": "Home & Garden", "description": "Home and garden supplies"},
        {"name": "Sports", "description": "Sports equipment and gear"},
        {"name": "Food & Beverages", "description": "Food and beverage products"},
        {"name": "Beauty", "description": "Beauty and personal care"},
    ]
    
    for cat_data in categories_data:
        existing = Category.query.filter_by(name=cat_data["name"]).first()
        if not existing:
            cat = Category(**cat_data)
            db.session.add(cat)
    
    db.session.commit()
    print("✓ Categories seeded")


def seed_products(db):
    """Seed products"""
    products_data = [
        {
            "name": "Wireless Headphones",
            "sku": "ELEC-001",
            "description": "Premium wireless headphones with noise cancellation",
            "category_id": 1,
            "price": 199.99,
            "quantity": 50,
            "is_active": True,
        },
        {
            "name": "USB-C Cable",
            "sku": "ELEC-002",
            "description": "High-speed USB-C charging cable",
            "category_id": 1,
            "price": 19.99,
            "quantity": 200,
            "is_active": True,
        },
        {
            "name": "T-Shirt",
            "sku": "CLTH-001",
            "description": "100% cotton comfortable t-shirt",
            "category_id": 2,
            "price": 29.99,
            "quantity": 100,
            "is_active": True,
        },
        {
            "name": "Yoga Mat",
            "sku": "SPRT-001",
            "description": "Non-slip yoga exercise mat",
            "category_id": 4,
            "price": 49.99,
            "quantity": 75,
            "is_active": True,
        },
        {
            "name": "Coffee Maker",
            "sku": "HOME-001",
            "description": "Automatic coffee maker, 12-cup capacity",
            "category_id": 3,
            "price": 89.99,
            "quantity": 30,
            "is_active": True,
        },
    ]
    
    for prod_data in products_data:
        existing = Product.query.filter_by(sku=prod_data["sku"]).first()
        if not existing:
            prod = Product(**prod_data)
            db.session.add(prod)
    
    db.session.commit()
    print("✓ Products seeded")


def seed_addresses(db):
    """Seed addresses"""
    users = User.query.all()
    
    for user in users[:1]:  # Add address for first user
        existing = Address.query.filter_by(user_id=user.id).first()
        if not existing:
            addr = Address(
                user_id=user.id,
                title="Main Office",
                gov_id=1,
                address_line1="123 Industrial Area",
                address_line2="Building 5",
                city="Cairo",
                postal_code="11111",
                is_default=True,
            )
            db.session.add(addr)
    
    db.session.commit()
    print("✓ Addresses seeded")


def seed_carts(db):
    """Seed shopping carts (optional)"""
    users = User.query.all()
    products = Product.query.all()
    
    for user in users[:1]:
        # Create or get cart
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.flush()
        
        # Add item if not exists
        if products and not CartItem.query.filter_by(cart_id=cart.id).first():
            item = CartItem(
                cart_id=cart.id,
                product_id=products[0].id,
                quantity=5,
            )
            db.session.add(item)
    
    db.session.commit()
    print("✓ Carts seeded")


def seed_wishlists(db):
    """Seed wishlists"""
    users = User.query.all()
    products = Product.query.all()
    
    for user in users[:1]:
        if products:
            # Add products to wishlist
            for product in products[:2]:
                existing = Wishlist.query.filter_by(
                    user_id=user.id, product_id=product.id
                ).first()
                if not existing:
                    wish = Wishlist(user_id=user.id, product_id=product.id)
                    db.session.add(wish)
    
    db.session.commit()
    print("✓ Wishlists seeded")


def seed_orders(db):
    """Seed sample orders"""
    users = User.query.all()
    products = Product.query.all()
    
    if not users or not products:
        return
    
    user = users[0]
    
    # Create order
    order = Order.query.filter_by(user_id=user.id).first()
    if not order:
        order = Order(
            user_id=user.id,
            address_id=None,  # Will set if address exists
            status="pending",
            total_amount=0,
        )
        
        # Set address if exists
        address = Address.query.filter_by(user_id=user.id).first()
        if address:
            order.address_id = address.id
        
        db.session.add(order)
        db.session.flush()
        
        # Add order items
        total = 0
        for product in products[:2]:
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=5,
                price=product.price,
            )
            db.session.add(item)
            total += item.quantity * item.price
        
        order.total_amount = total
    
    db.session.commit()
    print("✓ Orders seeded")


def seed_reviews(db):
    """Seed product reviews"""
    users = User.query.all()
    products = Product.query.all()
    
    if not users or not products:
        return
    
    for user in users[:1]:
        for product in products[:1]:
            existing = ProductReview.query.filter_by(
                user_id=user.id, product_id=product.id
            ).first()
            if not existing:
                review = ProductReview(
                    user_id=user.id,
                    product_id=product.id,
                    rating=5,
                    review="Great product! Highly recommended.",
                )
                db.session.add(review)
    
    db.session.commit()
    print("✓ Reviews seeded")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("TORIDA Database Seeding")
    print("=" * 60)
    
    app = create_app_context()
    
    with app.app_context():
        print("\nInitializing database...\n")
        
        # Check if tables exist
        inspector = db.inspect(db.engine)
        if not inspector.get_table_names():
            print("✗ Error: Database tables don't exist")
            print("  Run 'python -c \"from app import db, create_app; app = create_app(); db.create_all()\"' first")
            return False
        
        print("Running seed operations:\n")
        
        try:
            seed_user_types(db)
            seed_governorates(db)
            seed_test_users(db)
            seed_roles(db)
            seed_permissions(db)
            seed_categories(db)
            seed_products(db)
            seed_addresses(db)
            seed_carts(db)
            seed_wishlists(db)
            seed_orders(db)
            seed_reviews(db)
            
            print("\n" + "=" * 60)
            print("✓ Database seeding completed successfully!")
            print("=" * 60)
            print("\n✓ Test Account:")
            print("  Email: john.doe@example.com")
            print("  Password: Password123!")
            print("\nYou can now use this account in Postman:")
            print("  1. Go to Auth → POST /api/auth/login")
            print("  2. Run the request")
            print("  3. Token will be auto-captured")
            print("  4. All other endpoints will work!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error during seeding: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
