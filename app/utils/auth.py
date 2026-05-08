"""
TORIDA Authentication Utilities
================================
JWT token handling and password hashing functions.
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app, g
from typing import Optional, Dict, Any, Tuple

from app.utils.response import error_response, unauthorized_response


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(
    user_id: int,
    user_type: int,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User's ID
        user_type: User's type ID (1=Supplier, 2=Retailer, 3=Company)
        additional_claims: Optional additional claims
        
    Returns:
        JWT access token string
    """
    expires = datetime.utcnow() + timedelta(
        seconds=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)
    )
    
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'type': 'access',
        'exp': expires,
        'iat': datetime.utcnow()
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    secret = current_app.config.get('JWT_SECRET_KEY')
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    
    return jwt.encode(payload, secret, algorithm=algorithm)


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: User's ID
        
    Returns:
        JWT refresh token string
    """
    expires = datetime.utcnow() + timedelta(
        seconds=current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000)
    )
    
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': expires,
        'iat': datetime.utcnow()
    }
    
    secret = current_app.config.get('JWT_SECRET_KEY')
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    
    return jwt.encode(payload, secret, algorithm=algorithm)


def verify_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Tuple of (is_valid, decoded_payload_or_error)
    """
    try:
        secret = current_app.config.get('JWT_SECRET_KEY')
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, {'error': 'Token has expired'}
    except jwt.InvalidTokenError as e:
        return False, {'error': f'Invalid token: {str(e)}'}


def get_current_user():
    """
    Get the current authenticated user from the request.
    
    Returns:
        User model instance or None
    """
    return getattr(g, 'current_user', None)


def extract_token_from_request() -> Optional[str]:
    """
    Extract JWT token from the request.
    
    Checks:
    1. Authorization header (Bearer token)
    2. Query parameter (token)
    
    Returns:
        Token string or None
    """
    # Check Authorization header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Check query parameter
    token = request.args.get('token')
    if token:
        return token
    
    return None


def token_required(f):
    """
    Decorator to require a valid JWT token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token_from_request()
        
        if not token:
            return unauthorized_response("Authentication token is required")
        
        is_valid, result = verify_token(token)
        
        if not is_valid:
            return unauthorized_response(result.get('error', 'Invalid token'))
        
        # Store user info in Flask's g object
        g.current_user_id = result.get('user_id')
        g.current_user_type = result.get('user_type')
        g.token_payload = result
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator to require admin role.
    Note: This checks if the user has admin role assigned.
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        from app.models import User, UserRole, Role
        
        user_id = g.current_user_id
        
        # Check if user has admin role
        admin_role = Role.query.filter_by(role_name='Admin').first()
        if admin_role:
            user_role = UserRole.query.filter_by(
                user_id=user_id, 
                role_id=admin_role.id
            ).first()
            
            if user_role:
                return f(*args, **kwargs)
        
        return error_response("Admin access required", 403)
    
    return decorated


def seller_required(f):
    """
    Decorator to require seller role (Supplier or Company).
    Only users with type_id in (1, 3) can sell.
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        user_type = g.current_user_type
        
        if user_type not in [1, 3]:  # Supplier or Company
            return error_response("Seller access required (Supplier or Company)", 403)
        
        return f(*args, **kwargs)
    
    return decorated


def buyer_required(f):
    """
    Decorator to require buyer role (Retailer).
    Only users with type_id = 2 can buy.
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        user_type = g.current_user_type
        
        if user_type != 2:  # Retailer
            return error_response("Buyer access required (Retailer)", 403)
        
        return f(*args, **kwargs)
    
    return decorated


def permission_required(permission_name):
    """
    Decorator factory that checks whether the current user holds a specific
    permission through any of their assigned roles.

    Usage:
        @role_bp.route('/admin-settings', methods=['GET'])
        @permission_required('settings:read')
        def admin_settings():
            ...

    The decorator automatically applies @token_required so you do NOT need
    to stack both decorators on the same view.
    """
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            from app.services.role_service import user_has_permission

            user_id = g.current_user_id

            if not user_has_permission(user_id, permission_name):
                return error_response(
                    f"Permission '{permission_name}' is required",
                    403,
                    code="PERMISSION_DENIED"
                )

            return f(*args, **kwargs)
        return decorated
    return decorator


def load_user_from_token():
    """
    Load the full user object from the token.
    Must be used after token_required decorator.
    
    Returns:
        User model instance or None
    """
    from app.models import User
    
    user_id = getattr(g, 'current_user_id', None)
    if user_id:
        return User.query.get(user_id)
    return None
