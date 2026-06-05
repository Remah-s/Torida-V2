"""
User Routes
===========
Routes for user management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import User, UserType, Governorate, UserRole, Role
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_email, validate_phone, validate_required_fields, validate_pagination
from app.utils.auth import hash_password, token_required, admin_required

user_bp = Blueprint('users', __name__, url_prefix='/api/users')


@user_bp.route('', methods=['GET'])
@token_required
def get_users():
    """Get all users with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    # Filters
    type_id = request.args.get('type_id', type=int)
    gov_id = request.args.get('gov_id', type=int)
    is_active = request.args.get('is_active', type=str)
    search = request.args.get('search', type=str)
    
    query = User.query
    
    if type_id:
        query = query.filter_by(type_id=type_id)
    
    if gov_id:
        query = query.filter_by(gov_id=gov_id)
    
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active_bool)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                User.full_name.ilike(search_filter),
                User.email.ilike(search_filter),
                User.phone.ilike(search_filter)
            )
        )
    
    # Order by created_at descending
    query = query.order_by(User.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    users = [user.to_dict() for user in pagination.items]
    
    return paginated_response(users, page, per_page, pagination.total)


@user_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID."""
    user = User.query.get(user_id)
    
    if not user:
        return not_found_response("User not found")
    
    return success_response(user.to_dict(include_sensitive=True))


@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update user."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    user = User.query.get(user_id)
    
    if not user:
        return not_found_response("User not found")
    
    # Only allow users to update their own profile or admin
    current_user_id = g.current_user_id
    if current_user_id != user_id:
        # Check if admin by querying the DB
        from app.models import UserRole, Role
        admin_role = Role.query.filter_by(role_name='Admin').first()
        is_admin = False
        if admin_role:
            is_admin = UserRole.query.filter_by(
                user_id=current_user_id, role_id=admin_role.id
            ).first() is not None
        if not is_admin:
            return error_response("Not authorized to update this user", 403)
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    if 'email' in data:
        is_valid, error_msg = validate_email(data['email'])
        if not is_valid:
            return error_response(error_msg, 400)
        
        # Check if email is taken by another user
        existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
        if existing:
            return error_response("Email already in use", 400)
        user.email = data['email']
    
    if 'phone' in data:
        is_valid, error_msg = validate_phone(data['phone'])
        if not is_valid:
            return error_response(error_msg, 400)
        
        # Check if phone is taken by another user
        existing = User.query.filter(User.phone == data['phone'], User.id != user_id).first()
        if existing:
            return error_response("Phone already in use", 400)
        user.phone = data['phone']
    
    if 'gov_id' in data:
        governorate = Governorate.query.get(data['gov_id'])
        if not governorate:
            return error_response("Invalid governorate", 400)
        user.gov_id = data['gov_id']
    
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    
    try:
        db.session.commit()
        return success_response(user.to_dict(), "User updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    """Delete (deactivate) user."""
    from flask import g
    user = User.query.get(user_id)
    
    if not user:
        return not_found_response("User not found")
    
    # Only the user themselves or an admin can deactivate
    current_user_id = g.current_user_id
    if current_user_id != user_id:
        from app.models import UserRole, Role
        admin_role = Role.query.filter_by(role_name='Admin').first()
        is_admin = False
        if admin_role:
            is_admin = UserRole.query.filter_by(
                user_id=current_user_id, role_id=admin_role.id
            ).first() is not None
        if not is_admin:
            return error_response("Not authorized to deactivate this user", 403)
    
    # Soft delete - deactivate instead of actual delete
    user.is_active = False
    
    try:
        db.session.commit()
        return success_response(message="User deactivated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Deactivation failed: {str(e)}", 500)


@user_bp.route('/<int:user_id>/roles', methods=['GET'])
@token_required
def get_user_roles(user_id):
    """Get user's roles."""
    from app.services.role_service import get_roles_for_user

    roles, err = get_roles_for_user(user_id)
    if err:
        return not_found_response(err)
    return success_response(roles)


@user_bp.route('/<int:user_id>/roles', methods=['POST'])
@admin_required
def assign_role(user_id):
    """Assign role to user."""
    from app.services.role_service import assign_role_to_user

    data = request.get_json()
    if not data or not data.get('role_id'):
        return error_response("role_id is required", 400)

    try:
        rid = int(data['role_id'])
    except (TypeError, ValueError):
        return error_response("role_id must be an integer", 400)

    ok, err = assign_role_to_user(user_id, rid)
    if not ok:
        status = 404 if "not found" in err.lower() else 400
        return error_response(err, status)

    return success_response(message="Role assigned successfully")


@user_bp.route('/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@admin_required
def remove_role(user_id, role_id):
    """Remove role from user."""
    from app.services.role_service import remove_role_from_user

    ok, err = remove_role_from_user(user_id, role_id)
    if not ok:
        status = 404 if "not found" in err.lower() else 500
        return error_response(err, status)

    return success_response(message="Role removed successfully")


@user_bp.route('/<int:user_id>/addresses', methods=['GET'])
@token_required
def get_user_addresses(user_id):
    """Get user's addresses."""
    from app.models import Address
    user = User.query.get(user_id)
    
    if not user:
        return not_found_response("User not found")
    
    addresses = [addr.to_dict() for addr in user.addresses]
    
    return success_response(addresses)


@user_bp.route('/<int:user_id>/business-profile', methods=['GET'])
@token_required
def get_user_business_profile(user_id):
    """Get user's business profile."""
    from app.models import BusinessProfile
    user = User.query.get(user_id)
    
    if not user:
        return not_found_response("User not found")
    
    if not user.business_profile:
        return not_found_response("Business profile not found")
    
    return success_response(user.business_profile.to_dict())
