"""
Role Routes
===========
RESTful routes for role management, role-permission assignments, and user-role
management.

Endpoints
---------
Roles
  GET    /api/roles                                   — List roles (paginated)
  GET    /api/roles/<id>                               — Get single role (with permissions)
  POST   /api/roles                                   — Create role
  PUT    /api/roles/<id>                               — Update role
  DELETE /api/roles/<id>                               — Delete role

Role ↔ Permission pivot
  GET    /api/roles/<id>/permissions                  — List permissions for role
  POST   /api/roles/<id>/permissions                  — Assign one permission
  POST   /api/roles/<id>/permissions/bulk             — Assign many permissions
  PUT    /api/roles/<id>/permissions                  — Replace all permissions
  DELETE /api/roles/<id>/permissions/<perm_id>        — Remove one permission

User ↔ Role pivot
  GET    /api/roles/users/<user_id>                   — List roles for user
  POST   /api/roles/users/<user_id>                   — Assign one role
  POST   /api/roles/users/<user_id>/bulk              — Assign many roles
  DELETE /api/roles/users/<user_id>/<role_id>         — Remove one role
"""
from flask import Blueprint, request

from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination
from app.utils.auth import token_required, admin_required

from app.services.role_service import (
    # Role CRUD
    get_all_roles,
    get_role_by_id,
    create_role as svc_create_role,
    update_role as svc_update_role,
    delete_role as svc_delete_role,
    # Role-Permission
    get_permissions_for_role,
    assign_permission_to_role,
    assign_permissions_bulk,
    remove_permission_from_role,
    replace_permissions_for_role,
    # User-Role
    get_roles_for_user,
    assign_role_to_user,
    assign_roles_bulk,
    remove_role_from_user,
)

role_bp = Blueprint('roles', __name__, url_prefix='/api/roles')


# ═══════════════════════════════════════════════════════════════════════════
# Role CRUD
# ═══════════════════════════════════════════════════════════════════════════

@role_bp.route('', methods=['GET'])
@token_required
def get_roles():
    """Get all roles with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    page, per_page = validate_pagination(page, per_page)

    pagination = get_all_roles(page, per_page)
    roles = [r.to_dict() for r in pagination.items]

    return paginated_response(roles, page, per_page, pagination.total)


@role_bp.route('/<int:role_id>', methods=['GET'])
@token_required
def get_role(role_id):
    """Get role by ID (includes permissions)."""
    role = get_role_by_id(role_id)
    if not role:
        return not_found_response("Role not found")
    return success_response(role.to_dict_with_permissions())


@role_bp.route('', methods=['POST'])
@token_required
def create_role():
    """
    Create a new role.

    Body: { "role_name": "..." }

    The MySQL trigger `trg_roles_custom_id` auto-generates the custom_id
    (ROL-XXXXX) using the role_sequences counter row.
    """
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400, code="MISSING_BODY")

    is_valid, errors = validate_required_fields(data, ['role_name'])
    if not is_valid:
        return validation_error_response(errors)

    role, err = svc_create_role(data['role_name'])
    if err:
        return error_response(err, 400, code="ROLE_CREATE_FAILED")

    return created_response(role.to_dict(), "Role created successfully")


@role_bp.route('/<int:role_id>', methods=['PUT'])
@token_required
def update_role(role_id):
    """Update role."""
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400, code="MISSING_BODY")

    role, err = svc_update_role(role_id, data)
    if err:
        status = 404 if "not found" in err.lower() else 400
        return error_response(err, status, code="ROLE_UPDATE_FAILED")

    return success_response(role.to_dict(), "Role updated successfully")


@role_bp.route('/<int:role_id>', methods=['DELETE'])
@token_required
def delete_role(role_id):
    """Delete role (cascades to role_permissions and user_roles)."""
    ok, err = svc_delete_role(role_id)
    if not ok:
        status = 404 if "not found" in err.lower() else 500
        return error_response(err, status, code="ROLE_DELETE_FAILED")

    return success_response(message="Role deleted successfully")


# ═══════════════════════════════════════════════════════════════════════════
# Role ↔ Permission pivot
# ═══════════════════════════════════════════════════════════════════════════

@role_bp.route('/<int:role_id>/permissions', methods=['GET'])
@token_required
def get_role_permissions(role_id):
    """Get permissions for a role."""
    permissions, err = get_permissions_for_role(role_id)
    if err:
        return not_found_response(err)
    return success_response(permissions)


@role_bp.route('/<int:role_id>/permissions', methods=['POST'])
@token_required
def assign_permission(role_id):
    """
    Assign a single permission to a role.

    Body: { "permission_id": <int> }
    """
    data = request.get_json()
    if not data or not data.get('permission_id'):
        return error_response("permission_id is required", 400, code="MISSING_FIELD")

    try:
        pid = int(data['permission_id'])
    except (TypeError, ValueError):
        return error_response("permission_id must be an integer", 400, code="INVALID_FIELD")

    ok, err = assign_permission_to_role(role_id, pid)
    if not ok:
        status = 404 if "not found" in err.lower() else 400
        return error_response(err, status, code="PERM_ASSIGN_FAILED")

    return success_response(message="Permission assigned successfully")


@role_bp.route('/<int:role_id>/permissions/bulk', methods=['POST'])
@token_required
def bulk_assign_permissions(role_id):
    """
    Assign multiple permissions to a role in one request.

    Body: { "permission_ids": [1, 2, 3] }
    """
    data = request.get_json()
    if not data or not isinstance(data.get('permission_ids'), list):
        return error_response(
            "permission_ids (array) is required", 400, code="MISSING_FIELD"
        )

    if len(data['permission_ids']) == 0:
        return error_response(
            "permission_ids must not be empty", 400, code="EMPTY_ARRAY"
        )

    result, err = assign_permissions_bulk(role_id, data['permission_ids'])
    if err:
        status = 404 if "not found" in err.lower() else 500
        return error_response(err, status, code="PERM_BULK_FAILED")

    return success_response(result, "Bulk assignment complete")


@role_bp.route('/<int:role_id>/permissions', methods=['PUT'])
@token_required
def set_role_permissions(role_id):
    """
    Replace ALL permissions for a role with the provided set.

    Body: { "permission_ids": [1, 2, 3] }
    """
    data = request.get_json()
    if not data or not isinstance(data.get('permission_ids'), list):
        return error_response(
            "permission_ids (array) is required", 400, code="MISSING_FIELD"
        )

    permissions, err = replace_permissions_for_role(role_id, data['permission_ids'])
    if err:
        status = 404 if "not found" in err.lower() else 400
        return error_response(err, status, code="PERM_REPLACE_FAILED")

    return success_response(permissions, "Permissions replaced successfully")


@role_bp.route('/<int:role_id>/permissions/<int:permission_id>', methods=['DELETE'])
@token_required
def remove_permission(role_id, permission_id):
    """Remove a single permission from a role."""
    ok, err = remove_permission_from_role(role_id, permission_id)
    if not ok:
        status = 404 if "not found" in err.lower() else 500
        return error_response(err, status, code="PERM_REMOVE_FAILED")

    return success_response(message="Permission removed successfully")


# ═══════════════════════════════════════════════════════════════════════════
# User ↔ Role pivot  (also reachable via /api/users/<id>/roles in user_routes)
# ═══════════════════════════════════════════════════════════════════════════

@role_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def list_user_roles(user_id):
    """List all roles assigned to a user."""
    roles, err = get_roles_for_user(user_id)
    if err:
        return not_found_response(err)
    return success_response(roles)


@role_bp.route('/users/<int:user_id>', methods=['POST'])
@token_required
def assign_user_role(user_id):
    """
    Assign a single role to a user.

    Body: { "role_id": <int> }
    """
    data = request.get_json()
    if not data or not data.get('role_id'):
        return error_response("role_id is required", 400, code="MISSING_FIELD")

    try:
        rid = int(data['role_id'])
    except (TypeError, ValueError):
        return error_response("role_id must be an integer", 400, code="INVALID_FIELD")

    ok, err = assign_role_to_user(user_id, rid)
    if not ok:
        status = 404 if "not found" in err.lower() else 400
        return error_response(err, status, code="ROLE_ASSIGN_FAILED")

    return success_response(message="Role assigned to user successfully")


@role_bp.route('/users/<int:user_id>/bulk', methods=['POST'])
@token_required
def bulk_assign_user_roles(user_id):
    """
    Assign multiple roles to a user.

    Body: { "role_ids": [1, 2, 3] }
    """
    data = request.get_json()
    if not data or not isinstance(data.get('role_ids'), list):
        return error_response(
            "role_ids (array) is required", 400, code="MISSING_FIELD"
        )

    if len(data['role_ids']) == 0:
        return error_response(
            "role_ids must not be empty", 400, code="EMPTY_ARRAY"
        )

    result, err = assign_roles_bulk(user_id, data['role_ids'])
    if err:
        status = 404 if "not found" in err.lower() else 500
        return error_response(err, status, code="ROLE_BULK_FAILED")

    return success_response(result, "Bulk role assignment complete")


@role_bp.route('/users/<int:user_id>/<int:role_id>', methods=['DELETE'])
@token_required
def remove_user_role(user_id, role_id):
    """Remove a role from a user."""
    ok, err = remove_role_from_user(user_id, role_id)
    if not ok:
        status = 404 if "not found" in err.lower() else 500
        return error_response(err, status, code="ROLE_REMOVE_FAILED")

    return success_response(message="Role removed from user successfully")
