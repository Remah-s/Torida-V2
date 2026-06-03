"""
TORIDA Flask Application Factory
=================================
B2B Marketplace Backend for Egypt.
"""
import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import cloudinary

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

    cors_origins = app.config.get('CORS_ORIGINS') or '*'
    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize database
    init_db(app)
    
    # Initialize Cloudinary
    cloudinary.config(
        cloud_name=app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=app.config.get('CLOUDINARY_API_KEY'),
        api_secret=app.config.get('CLOUDINARY_API_SECRET')
    )
    
    # Set up logging for Cloudinary
    logger = logging.getLogger(__name__)
    if app.config.get('CLOUDINARY_CLOUD_NAME'):
        logger.info("Cloudinary configured successfully")
    else:
        logger.warning("Cloudinary not configured - image uploads may fail")
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    # Register security headers
    register_security_headers(app)
    
    # Create upload folder if not exists
    upload_folder = app.config.get('UPLOAD_FOLDER', '/tmp/uploads')
    try:
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
    except Exception as e:
        app.logger.warning(f"Could not create upload folder {upload_folder}: {str(e)}")
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint."""
        return jsonify({
            'name': 'TORIDA API',
            'message': 'API running successfully',
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

    @app.route('/uploads/<path:filename>', methods=['GET'])
    def serve_upload(filename):
        """Serve uploaded files."""
        upload_root = os.path.abspath(app.config.get('UPLOAD_FOLDER', 'uploads'))
        return send_from_directory(upload_root, filename)
    
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
    from app.routes.admin_routes import admin_bp
    
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
    
    # Admin routes
    app.register_blueprint(admin_bp)


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
        # Don't log HTTPException as unhandled
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            return jsonify({
                'success': False,
                'message': error.description
            }), error.code
        import traceback
        tb = traceback.format_exc()
        app.logger.error(f"Unhandled exception: {str(error)}\n{tb}")
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
        from app.models import Governorate, UserType, Role, Permission, RoleSequence
        
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
            
            # Seed role_sequences — upsert counter row (id=1)
            seq_row = RoleSequence.query.get(1)
            if not seq_row:
                seq_row = RoleSequence(id=1, sequence=0)
                db.session.add(seq_row)
            
            # Seed roles
            roles = ['Admin', 'Manager', 'Editor', 'Viewer']
            for role_name in roles:
                if not Role.query.filter_by(role_name=role_name).first():
                    role = Role(role_name=role_name)
                    db.session.add(role)
            
            # Seed permissions (resource:action format)
            permissions = [
                'users:create', 'users:read', 'users:write', 'users:delete',
                'products:create', 'products:read', 'products:write', 'products:delete',
                'orders:create', 'orders:read', 'orders:write', 'orders:cancel',
                'roles:manage', 'permissions:manage',
                'reports:read', 'settings:manage'
            ]
            
            for perm_name in permissions:
                if not Permission.query.filter_by(permission_name=perm_name).first():
                    perm = Permission(permission_name=perm_name)
                    db.session.add(perm)
            
            db.session.commit()
            print('Database seeded with initial data.')


def register_security_headers(app):
    """Register security headers for all responses."""
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        return response
