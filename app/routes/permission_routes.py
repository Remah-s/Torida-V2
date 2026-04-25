"""
Permission Routes
=================
Routes for permission management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Permission
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination
from app.utils.auth import token_required

permission_bp = Blueprint('permissions', __name__, url_prefix='/api/permissions')


@permission_bp.route('', methods=['GET'])
@token_required
def get_permissions():
    """Get all permissions with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    query = Permission.query.order_by(Permission.id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    permissions = [perm.to_dict() for perm in pagination.items]
    
    return paginated_response(permissions, page, per_page, pagination.total)


@permission_bp.route('/<int:permission_id>', methods=['GET'])
@token_required
def get_permission(permission_id):
    """Get permission by ID."""
    permission = Permission.query.get(permission_id)
    
    if not permission:
        return not_found_response("Permission not found")
    
    return success_response(permission.to_dict())


@permission_bp.route('', methods=['POST'])
@token_required
def create_permission():
    """Create a new permission."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['permission_name']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Check if permission name already exists
    if Permission.query.filter_by(permission_name=data['permission_name']).first():
        return error_response("Permission name already exists", 400)
    
    try:
        permission = Permission(permission_name=data['permission_name'])
        db.session.add(permission)
        db.session.commit()
        
        return created_response(permission.to_dict(), "Permission created successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Permission creation failed: {str(e)}", 500)


@permission_bp.route('/<int:permission_id>', methods=['PUT'])
@token_required
def update_permission(permission_id):
    """Update permission."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    permission = Permission.query.get(permission_id)
    
    if not permission:
        return not_found_response("Permission not found")
    
    if 'permission_name' in data:
        # Check if permission name is taken
        existing = Permission.query.filter(
            Permission.permission_name == data['permission_name'],
            Permission.id != permission_id
        ).first()
        if existing:
            return error_response("Permission name already exists", 400)
        permission.permission_name = data['permission_name']
    
    try:
        db.session.commit()
        return success_response(permission.to_dict(), "Permission updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@permission_bp.route('/<int:permission_id>', methods=['DELETE'])
@token_required
def delete_permission(permission_id):
    """Delete permission."""
    permission = Permission.query.get(permission_id)
    
    if not permission:
        return not_found_response("Permission not found")
    
    try:
        db.session.delete(permission)
        db.session.commit()
        return success_response(message="Permission deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)
