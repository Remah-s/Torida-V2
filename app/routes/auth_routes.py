"""
Authentication Routes
=====================
Routes for user authentication (register, login, logout, OTP verification).
"""
from flask import Blueprint, request, current_app
from datetime import datetime, timedelta

from app.database import db
from app.models import User, UserType, Governorate, OTP, CodeSequence
from app.utils.response import (
    success_response, error_response, created_response,
    unauthorized_response, validation_error_response
)
from app.utils.validators import validate_email, validate_phone, validate_password, validate_required_fields
from app.utils.auth import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, verify_token, token_required
)
from app.utils.helpers import generate_otp
from app.services.email_service import EmailService
from app.services.otp_service import OTPService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    # Validate required fields
    required_fields = ['full_name', 'phone', 'email', 'password', 'type_id', 'gov_id']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Validate email
    is_valid, error_msg = validate_email(data['email'])
    if not is_valid:
        return error_response(error_msg, 400)
    
    # Validate phone
    is_valid, error_msg = validate_phone(data['phone'])
    if not is_valid:
        return error_response(error_msg, 400)
    
    # Validate password
    is_valid, error_msg = validate_password(data['password'])
    if not is_valid:
        return error_response(error_msg, 400)
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return error_response("Email already registered", 400)
    
    # Check if phone already exists
    if User.query.filter_by(phone=data['phone']).first():
        return error_response("Phone number already registered", 400)
    
    # Validate user type
    user_type = UserType.query.get(data['type_id'])
    if not user_type:
        return error_response("Invalid user type", 400)
    
    # Validate governorate
    governorate = Governorate.query.get(data['gov_id'])
    if not governorate:
        return error_response("Invalid governorate", 400)
    
    try:
        # Generate user code
        type_id = data['type_id']
        gov_id = data['gov_id']
        
        # Get or create code sequence
        code_seq = CodeSequence.query.filter_by(type_id=type_id, gov_id=gov_id).first()
        if not code_seq:
            code_seq = CodeSequence(type_id=type_id, gov_id=gov_id, sequence=0)
            db.session.add(code_seq)
            db.session.flush()
        
        code_seq.sequence += 1
        sequence = code_seq.sequence
        
        # Generate code and custom_id
        code = f"{type_id}{gov_id}{str(sequence).zfill(3)}"
        
        if type_id == 1:
            custom_id = f"SUP-{code}"
        elif type_id == 2:
            custom_id = f"RET-{code}"
        elif type_id == 3:
            custom_id = f"COM-{code}"
        else:
            custom_id = f"USR-{code}"
        
        # Create user
        user = User(
            code=code,
            custom_id=custom_id,
            full_name=data['full_name'],
            phone=data['phone'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            type_id=type_id,
            gov_id=gov_id,
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        EmailService.send_welcome_email(user.email, user.full_name)
        
        # Generate OTP for email verification
        OTPService.generate_and_send_otp(user, "email_verification")
        
        # Create tokens
        access_token = create_access_token(user.id, user.type_id)
        refresh_token = create_refresh_token(user.id)
        
        return created_response({
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': 'Registration successful. Please verify your email.'
        }, "User registered successfully")
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {str(e)}", 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return error_response("Email and password are required", 400)
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return unauthorized_response("Invalid credentials")
    
    # Check if user is active
    if not user.is_active:
        return error_response("Account is deactivated", 403)
    
    # Verify password
    if not verify_password(data['password'], user.password_hash):
        return unauthorized_response("Invalid credentials")
    
    # Create tokens
    access_token = create_access_token(user.id, user.type_id)
    refresh_token = create_refresh_token(user.id)
    
    return success_response({
        'user': user.to_dict(include_sensitive=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    }, "Login successful")


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (client should discard tokens)."""
    return success_response(message="Logged out successfully")


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token."""
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        return error_response("Refresh token is required", 400)
    
    # Verify refresh token
    is_valid, result = verify_token(data['refresh_token'])
    
    if not is_valid:
        return unauthorized_response(result.get('error', 'Invalid refresh token'))
    
    if result.get('type') != 'refresh':
        return error_response("Invalid token type", 400)
    
    # Get user
    user_id = result.get('user_id')
    user = User.query.get(user_id)
    
    if not user or not user.is_active:
        return unauthorized_response("User not found or inactive")
    
    # Create new tokens
    access_token = create_access_token(user.id, user.type_id)
    new_refresh_token = create_refresh_token(user.id)
    
    return success_response({
        'access_token': access_token,
        'refresh_token': new_refresh_token
    }, "Token refreshed successfully")


@auth_bp.route('/verify-email', methods=['POST'])
@token_required
def verify_email():
    """Verify email with OTP."""
    from flask import g
    data = request.get_json()
    
    if not data or not data.get('otp'):
        return error_response("OTP is required", 400)
    
    user_id = g.current_user_id
    
    # Verify OTP
    is_valid, message = OTPService.verify_otp(user_id, data['otp'])
    
    if not is_valid:
        return error_response(message, 400)
    
    return success_response(message=message)


@auth_bp.route('/resend-otp', methods=['POST'])
@token_required
def resend_otp():
    """Resend OTP for email verification."""
    from flask import g
    user_id = g.current_user_id
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    success, result = OTPService.resend_otp(user, "verification")
    
    if not success:
        return error_response(result, 400)
    
    return success_response(message="OTP sent successfully")


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset."""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return error_response("Email is required", 400)
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        # Don't reveal if email exists or not
        return success_response(message="If the email exists, a password reset OTP has been sent")
    
    # Generate and send OTP
    success, result = OTPService.generate_and_send_otp(user, "password_reset")
    
    return success_response(message="If the email exists, a password reset OTP has been sent")


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with OTP."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required = ['email', 'otp', 'new_password']
    is_valid, errors = validate_required_fields(data, required)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Validate new password
    is_valid, error_msg = validate_password(data['new_password'])
    if not is_valid:
        return error_response(error_msg, 400)
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return error_response("Invalid request", 400)
    
    # Verify OTP
    is_valid, message = OTPService.verify_otp(user.id, data['otp'])
    
    if not is_valid:
        return error_response(message, 400)
    
    # Update password
    user.password_hash = hash_password(data['new_password'])
    db.session.commit()
    
    return success_response(message="Password reset successfully")


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change password for logged-in user."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required = ['current_password', 'new_password']
    is_valid, errors = validate_required_fields(data, required)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Validate new password
    is_valid, error_msg = validate_password(data['new_password'])
    if not is_valid:
        return error_response(error_msg, 400)
    
    user_id = g.current_user_id
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    # Verify current password
    if not verify_password(data['current_password'], user.password_hash):
        return error_response("Current password is incorrect", 400)
    
    # Update password
    user.password_hash = hash_password(data['new_password'])
    db.session.commit()
    
    return success_response(message="Password changed successfully")


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current authenticated user."""
    from flask import g
    user_id = g.current_user_id
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    return success_response(user.to_dict(include_sensitive=True))
