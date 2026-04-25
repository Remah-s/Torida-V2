"""
TORIDA Flask Application Factory
=================================
B2B Marketplace Backend for Egypt.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import config
from app.database import db, init_db


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
        
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    # Create upload folder if not exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint."""
        return jsonify({
            'name': 'TORIDA API',
            'message': 'Welcome to TORIDA B2B Marketplace API. Visit /api for endpoint information.',
            'version': '1.0.0'
        })
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'TORIDA API',
            'version': '1.0.0'
        })
    
    # API info endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            'name': 'TORIDA API',
            'description': 'B2B Marketplace Backend for Egypt',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'roles': '/api/roles',
                'permissions': '/api/permissions',
                'governorates': '/api/governorates',
                'user_types': '/api/user-types',
                'business_profiles': '/api/business-profiles',
                'categories': '/api/categories',
                'products': '/api/products',
                'cart': '/api/cart',
                'wishlist': '/api/wishlist',
                'orders': '/api/orders',
                'payments': '/api/payments',
                'reviews': '/api/reviews',
                'notifications': '/api/notifications',
                'addresses': '/api/addresses'
            }
        })
    
    return app


def register_blueprints(app):
    """Register all blueprints with the application."""
    from app.routes import (
        auth_bp, user_bp, role_bp, permission_bp,
        governorate_bp, user_type_bp, business_profile_bp,
        category_bp, product_bp, cart_bp, wishlist_bp,
        order_bp, payment_bp, review_bp, notification_bp, address_bp
    )
    
    # Authentication routes
    app.register_blueprint(auth_bp)
    
    # User management routes
    app.register_blueprint(user_bp)
    
    # Role and permission routes
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    
    # Geographic routes
    app.register_blueprint(governorate_bp)
    
    # User type routes
    app.register_blueprint(user_type_bp)
    
    # Business profile routes
    app.register_blueprint(business_profile_bp)
    
    # Product routes
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    
    # Shopping routes
    app.register_blueprint(cart_bp)
    app.register_blueprint(wishlist_bp)
    
    # Order routes
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    
    # Review routes
    app.register_blueprint(review_bp)
    
    # Notification routes
    app.register_blueprint(notification_bp)
    
    # Address routes
    app.register_blueprint(address_bp)


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': 'Forbidden'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': 'Method not allowed'
        }), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'message': 'Unprocessable entity'
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f"Unhandled exception: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred'
        }), 500


def register_commands(app):
    """Register CLI commands."""
    
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database."""
        with app.app_context():
            db.create_all()
        print('Database initialized.')
    
    @app.cli.command('reset-db')
    def reset_db_command():
        """Reset the database (WARNING: deletes all data)."""
        with app.app_context():
            db.drop_all()
            db.create_all()
        print('Database reset.')
    
    @app.cli.command('seed-db')
    def seed_db_command():
        """Seed the database with initial data."""
        from app.models import Governorate, UserType, Role, Permission
        
        with app.app_context():
            # Seed governorates
            governorates = [
                (1, 'Cairo'), (2, 'Giza'), (3, 'Alexandria'),
                (4, 'Qalyubia'), (5, 'Port Said'), (6, 'Suez'),
                (7, 'Dakahlia'), (8, 'Sharqia'), (9, 'Gharbia'),
                (10, 'Kafr El Sheikh'), (11, 'Monufia'), (12, 'Beheira'),
                (13, 'Ismailia'), (14, 'Beni Suef'), (15, 'Fayoum'),
                (16, 'Minya'), (17, 'Assiut'), (18, 'Sohag'),
                (19, 'Qena'), (20, 'Luxor'), (21, 'Aswan'),
                (22, 'Red Sea'), (23, 'New Valley'), (24, 'Matrouh'),
                (25, 'North Sinai'), (26, 'South Sinai'), (27, 'Damietta')
            ]
            
            for gov_id, gov_name in governorates:
                if not Governorate.query.get(gov_id):
                    gov = Governorate(id=gov_id, gov_name=gov_name)
                    db.session.add(gov)
            
            # Seed user types
            user_types = [
                (1, 'Supplier', True, False),
                (2, 'Retailer', False, True),
                (3, 'Company', True, False)
            ]
            
            for type_id, type_name, can_sell, can_buy in user_types:
                if not UserType.query.get(type_id):
                    user_type = UserType(
                        id=type_id, 
                        type_name=type_name,
                        can_sell=can_sell,
                        can_buy=can_buy
                    )
                    db.session.add(user_type)
            
            # Seed roles
            roles = ['Admin', 'Manager', 'Editor', 'Viewer']
            for role_name in roles:
                if not Role.query.filter_by(role_name=role_name).first():
                    role = Role(role_name=role_name)
                    db.session.add(role)
            
            # Seed permissions
            permissions = [
                'create_users', 'edit_users', 'delete_users', 'view_users',
                'create_products', 'edit_products', 'delete_products', 'view_products',
                'create_orders', 'edit_orders', 'cancel_orders', 'view_orders',
                'manage_roles', 'manage_permissions', 'view_reports', 'manage_settings'
            ]
            
            for perm_name in permissions:
                if not Permission.query.filter_by(permission_name=perm_name).first():
                    perm = Permission(permission_name=perm_name)
                    db.session.add(perm)
            
            db.session.commit()
            print('Database seeded with initial data.')
