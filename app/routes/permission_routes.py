"""
Permission Routes
=================
RESTful routes for permission management.

Endpoints
---------
  GET    /api/permissions                 — List permissions (paginated)
  GET    /api/permissions/<id>            — Get single permission
  POST   /api/permissions                 — Create permission
  POST   /api/permissions/bulk            — Create many permissions
  PUT    /api/permissions/<id>            — Update permission
  DELETE /api/permissions/<id>            — Delete permission
"""
from flask import Blueprint, request

from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination
from app.utils.auth import token_required

from app.services.role_service import (
    get_all_permissions,
    get_permission_by_id,
    create_permission as svc_create_permission,
    update_permission as svc_update_permission,
    delete_permission as svc_delete_permission,
    create_permissions_bulk,
)

permission_bp = Blueprint('permissions', __name__, url_prefix='/api/permissions')


@permission_bp.route('', methods=['GET'])
@token_required
def get_permissions():
    """Get all permissions with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    page, per_page = validate_pagination(page, per_page)

    pagination = get_all_permissions(page, per_page)
    permissions = [p.to_dict() for p in pagination.items]

    return paginated_response(permissions, page, per_page, pagination.total)


@permission_bp.route('/<int:permission_id>', methods=['GET'])
@token_required
def get_permission(permission_id):
    """Get permission by ID."""
    perm = get_permission_by_id(permission_id)
    if not perm:
        return not_found_response("Permission not found")
    return success_response(perm.to_dict())


@permission_bp.route('', methods=['POST'])
@token_required
def create_permission():
    """
    Create a new permission.

    Body: { "permission_name": "resource:action" }
    """
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400, code="MISSING_BODY")

    is_valid, errors = validate_required_fields(data, ['permission_name'])
    if not is_valid:
        return validation_error_response(errors)

    perm, err = svc_create_permission(data['permission_name'])
    if err:
        return error_response(err, 400, code="PERM_CREATE_FAILED")

    return created_response(perm.to_dict(), "Permission created successfully")


@permission_bp.route('/bulk', methods=['POST'])
@token_required
def bulk_create_permissions():
    """
    Create multiple permissions in a single request.

    Body: { "permission_names": ["orders:read", "orders:write", ...] }
    """
    data = request.get_json()
    if not data or not isinstance(data.get('permission_names'), list):
        return error_response(
            "permission_names (array) is required", 400, code="MISSING_FIELD"
        )

    if len(data['permission_names']) == 0:
        return error_response(
            "permission_names must not be empty", 400, code="EMPTY_ARRAY"
        )

    result, err = create_permissions_bulk(data['permission_names'])
    if err:
        return error_response(err, 500, code="PERM_BULK_FAILED")

    return created_response(result, "Bulk permission creation complete")


@permission_bp.route('/<int:permission_id>', methods=['PUT'])
@token_required
def update_permission(permission_id):
    """Update permission."""
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400, code="MISSING_BODY")

    perm, err = svc_update_permission(permission_id, data)
    if err:
        status = 404 if "not found" in err.lower() else 400
        return error_response(err, status, code="PERM_UPDATE_FAILED")

    return success_response(perm.to_dict(), "Permission updated successfully")


@permission_bp.route('/<int:permission_id>', methods=['DELETE'])
@token_required
def delete_permission(permission_id):
    """Delete permission (cascades to role_permissions)."""
    ok, err = svc_delete_permission(permission_id)
    if not ok:
        status = 404 if "not found" in err.lower() else 500
        return error_response(err, status, code="PERM_DELETE_FAILED")

    return success_response(message="Permission deleted successfully")
