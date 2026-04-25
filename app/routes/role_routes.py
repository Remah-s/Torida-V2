"""
Role Routes
===========
Routes for role management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Role, Permission, RolePermission
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination
from app.utils.auth import token_required, admin_required

role_bp = Blueprint('roles', __name__, url_prefix='/api/roles')


@role_bp.route('', methods=['GET'])
@token_required
def get_roles():
    """Get all roles with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    query = Role.query.order_by(Role.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    roles = [role.to_dict() for role in pagination.items]
    
    return paginated_response(roles, page, per_page, pagination.total)


@role_bp.route('/<int:role_id>', methods=['GET'])
@token_required
def get_role(role_id):
    """Get role by ID."""
    role = Role.query.get(role_id)
    
    if not role:
        return not_found_response("Role not found")
    
    return success_response(role.to_dict_with_permissions())


@role_bp.route('', methods=['POST'])
@token_required
def create_role():
    """Create a new role."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['role_name']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Check if role name already exists
    if Role.query.filter_by(role_name=data['role_name']).first():
        return error_response("Role name already exists", 400)
    
    try:
        role = Role(role_name=data['role_name'])
        db.session.add(role)
        db.session.commit()
        
        # Update custom_id (trigger simulation)
        role.custom_id = f"ROL-{str(role.id).zfill(5)}"
        db.session.commit()
        
        return created_response(role.to_dict(), "Role created successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Role creation failed: {str(e)}", 500)


@role_bp.route('/<int:role_id>', methods=['PUT'])
@token_required
def update_role(role_id):
    """Update role."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    role = Role.query.get(role_id)
    
    if not role:
        return not_found_response("Role not found")
    
    if 'role_name' in data:
        # Check if role name is taken by another role
        existing = Role.query.filter(
            Role.role_name == data['role_name'],
            Role.id != role_id
        ).first()
        if existing:
            return error_response("Role name already exists", 400)
        role.role_name = data['role_name']
    
    try:
        db.session.commit()
        return success_response(role.to_dict(), "Role updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@role_bp.route('/<int:role_id>', methods=['DELETE'])
@token_required
def delete_role(role_id):
    """Delete role."""
    role = Role.query.get(role_id)
    
    if not role:
        return not_found_response("Role not found")
    
    try:
        db.session.delete(role)
        db.session.commit()
        return success_response(message="Role deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)


@role_bp.route('/<int:role_id>/permissions', methods=['GET'])
@token_required
def get_role_permissions(role_id):
    """Get permissions for a role."""
    role = Role.query.get(role_id)
    
    if not role:
        return not_found_response("Role not found")
    
    permissions = [rp.permission.to_dict() for rp in role.role_permissions]
    
    return success_response(permissions)


@role_bp.route('/<int:role_id>/permissions', methods=['POST'])
@token_required
def assign_permission(role_id):
    """Assign permission to role."""
    data = request.get_json()
    
    if not data or not data.get('permission_id'):
        return error_response("Permission ID is required", 400)
    
    role = Role.query.get(role_id)
    if not role:
        return not_found_response("Role not found")
    
    permission = Permission.query.get(data['permission_id'])
    if not permission:
        return not_found_response("Permission not found")
    
    # Check if already assigned
    existing = RolePermission.query.filter_by(
        role_id=role_id, 
        permission_id=data['permission_id']
    ).first()
    
    if existing:
        return error_response("Permission already assigned to role", 400)
    
    try:
        role_permission = RolePermission(
            role_id=role_id, 
            permission_id=data['permission_id']
        )
        db.session.add(role_permission)
        db.session.commit()
        return success_response(message="Permission assigned successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Permission assignment failed: {str(e)}", 500)


@role_bp.route('/<int:role_id>/permissions/<int:permission_id>', methods=['DELETE'])
@token_required
def remove_permission(role_id, permission_id):
    """Remove permission from role."""
    role_permission = RolePermission.query.filter_by(
        role_id=role_id, 
        permission_id=permission_id
    ).first()
    
    if not role_permission:
        return not_found_response("Permission assignment not found")
    
    try:
        db.session.delete(role_permission)
        db.session.commit()
        return success_response(message="Permission removed successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Permission removal failed: {str(e)}", 500)
