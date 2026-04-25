"""
TORIDA Routes Package
=====================
API route blueprints for the application.
"""
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.role_routes import role_bp
from app.routes.permission_routes import permission_bp
from app.routes.governorate_routes import governorate_bp
from app.routes.user_type_routes import user_type_bp
from app.routes.business_profile_routes import business_profile_bp
from app.routes.category_routes import category_bp
from app.routes.product_routes import product_bp
from app.routes.cart_routes import cart_bp
from app.routes.wishlist_routes import wishlist_bp
from app.routes.order_routes import order_bp
from app.routes.payment_routes import payment_bp
from app.routes.review_routes import review_bp
from app.routes.notification_routes import notification_bp
from app.routes.address_routes import address_bp

__all__ = [
    'auth_bp',
    'user_bp',
    'role_bp',
    'permission_bp',
    'governorate_bp',
    'user_type_bp',
    'business_profile_bp',
    'category_bp',
    'product_bp',
    'cart_bp',
    'wishlist_bp',
    'order_bp',
    'payment_bp',
    'review_bp',
    'notification_bp',
    'address_bp'
]
