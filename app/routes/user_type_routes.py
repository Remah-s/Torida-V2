"""
User Type Routes
================
Routes for user type management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import UserType
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, validation_error_response
)
from app.utils.validators import validate_required_fields
from app.utils.auth import token_required

user_type_bp = Blueprint('user_types', __name__, url_prefix='/api/user-types')


@user_type_bp.route('', methods=['GET'])
def get_user_types():
    """Get all user types."""
    user_types = UserType.query.order_by(UserType.id).all()
    
    return success_response([ut.to_dict() for ut in user_types])


@user_type_bp.route('/<int:type_id>', methods=['GET'])
def get_user_type(type_id):
    """Get user type by ID."""
    user_type = UserType.query.get(type_id)
    
    if not user_type:
        return not_found_response("User type not found")
    
    return success_response(user_type.to_dict())


@user_type_bp.route('', methods=['POST'])
@token_required
def create_user_type():
    """Create a new user type."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['type_name']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Check if user type name already exists
    if UserType.query.filter_by(type_name=data['type_name']).first():
        return error_response("User type name already exists", 400)
    
    try:
        user_type = UserType(
            type_name=data['type_name'],
            can_sell=data.get('can_sell', False),
            can_buy=data.get('can_buy', False)
        )
        db.session.add(user_type)
        db.session.commit()
        
        return created_response(user_type.to_dict(), "User type created successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"User type creation failed: {str(e)}", 500)


@user_type_bp.route('/<int:type_id>', methods=['PUT'])
@token_required
def update_user_type(type_id):
    """Update user type."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    user_type = UserType.query.get(type_id)
    
    if not user_type:
        return not_found_response("User type not found")
    
    if 'type_name' in data:
        # Check if user type name is taken
        existing = UserType.query.filter(
            UserType.type_name == data['type_name'],
            UserType.id != type_id
        ).first()
        if existing:
            return error_response("User type name already exists", 400)
        user_type.type_name = data['type_name']
    
    if 'can_sell' in data:
        user_type.can_sell = bool(data['can_sell'])
    
    if 'can_buy' in data:
        user_type.can_buy = bool(data['can_buy'])
    
    try:
        db.session.commit()
        return success_response(user_type.to_dict(), "User type updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@user_type_bp.route('/<int:type_id>', methods=['DELETE'])
@token_required
def delete_user_type(type_id):
    """Delete user type."""
    user_type = UserType.query.get(type_id)
    
    if not user_type:
        return not_found_response("User type not found")
    
    # Check if user type has users
    if user_type.users.count() > 0:
        return error_response("Cannot delete user type with associated users", 400)
    
    try:
        db.session.delete(user_type)
        db.session.commit()
        return success_response(message="User type deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)
