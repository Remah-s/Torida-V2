"""
Role Service
============
Business-logic layer for Roles, Permissions, Role-Permissions, and User-Roles.

Design decisions
----------------
* The MySQL trigger `trg_roles_custom_id` sets `roles.custom_id` on INSERT
  using the counter in `role_sequences` (id = 1).  We therefore:
    1. Do NOT set custom_id in application code when running against MySQL.
    2. After INSERT we `db.session.refresh(role)` to pull the trigger-generated
       value back into the ORM instance.
    3. A fallback path (`_ensure_custom_id`) is provided for engines without
       trigger support (e.g. SQLite during unit-tests).
* All write operations are wrapped in try / except so the caller (route) never
  needs to touch `db.session.rollback()`.
"""
from typing import Optional, Tuple, List, Dict, Any

from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.models.user import User

ADMIN_ROLE_NAME = 'Admin'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_mysql() -> bool:
    """Return True when the bound engine is MySQL / MariaDB."""
    try:
        engine_url = str(db.engine.url)
        return 'mysql' in engine_url.lower()
    except Exception:
        return False


def _ensure_custom_id(role: Role) -> None:
    """
    Fallback for non-MySQL engines (e.g. SQLite in tests).
    Manually generates ROL-XXXXX using the role_sequences table.
    On MySQL the BEFORE INSERT trigger handles this — this is a no-op.
    """
    if _is_mysql():
        # Trigger already set it; just refresh.
        db.session.refresh(role)
        return

    # App-level fallback: upsert sequence row and set custom_id
    from app.models.role_sequence import RoleSequence

    seq_row = RoleSequence.query.get(1)
    if seq_row is None:
        seq_row = RoleSequence(id=1, sequence=0)
        db.session.add(seq_row)
        db.session.flush()

    seq_row.sequence += 1
    role.custom_id = f"ROL-{str(seq_row.sequence).zfill(5)}"


def get_role_by_name(role_name: str) -> Optional[Role]:
    """Return a role by its name or None."""
    return Role.query.filter_by(role_name=role_name).first()


def _resolve_user(user_or_id) -> Optional[User]:
    """Resolve a user instance from either a model instance or user id."""
    if isinstance(user_or_id, User):
        return user_or_id
    return User.query.get(user_or_id)


def get_effective_permissions_for_user(user_or_id) -> List[dict]:
    """Return the distinct permissions granted to a user through all roles."""
    user = _resolve_user(user_or_id)
    if not user:
        return []

    permissions = (
        db.session.query(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .filter(UserRole.user_id == user.id)
        .distinct()
        .order_by(Permission.permission_name.asc())
        .all()
    )
    return [permission.to_dict() for permission in permissions]


def serialize_user_access(user: User) -> dict:
    """Return a dashboard-friendly snapshot of a user's roles and permissions."""
    data = user.to_dict(include_sensitive=True)
    effective_permissions = get_effective_permissions_for_user(user)

    data['is_admin'] = any(
        role.get('role_name') == ADMIN_ROLE_NAME for role in data.get('roles', [])
    )
    data['effective_permissions'] = effective_permissions
    data['effective_permission_names'] = [
        permission['permission_name'] for permission in effective_permissions
    ]
    data['roles_count'] = len(data.get('roles', []))
    data['permissions_count'] = len(effective_permissions)
    return data


# ---------------------------------------------------------------------------
# Role CRUD
# ---------------------------------------------------------------------------

def get_all_roles(page: int, per_page: int):
    """Return paginated roles."""
    query = Role.query.order_by(Role.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination


def get_role_by_id(role_id: int) -> Optional[Role]:
    """Return a single role or None."""
    return Role.query.get(role_id)


def create_role(role_name: str) -> Tuple[Optional[Role], Optional[str]]:
    """
    Create a new role.
    
    Returns:
        (Role, None)   on success
        (None, error)  on failure
    """
    role_name = role_name.strip()
    if not role_name:
        return None, "role_name is required"

    if len(role_name) > 100:
        return None, "role_name must be 100 characters or fewer"

    # Uniqueness check
    if Role.query.filter_by(role_name=role_name).first():
        return None, "Role name already exists"

    try:
        role = Role(role_name=role_name)
        db.session.add(role)
        db.session.flush()  # get auto-id before trigger fires on commit

        _ensure_custom_id(role)

        db.session.commit()
        db.session.refresh(role)  # pull trigger-generated custom_id
        return role, None
    except IntegrityError:
        db.session.rollback()
        return None, "Role name already exists"
    except Exception as exc:
        db.session.rollback()
        return None, f"Role creation failed: {str(exc)}"


def update_role(role_id: int, data: dict) -> Tuple[Optional[Role], Optional[str]]:
    """Update a role's editable fields."""
    role = Role.query.get(role_id)
    if not role:
        return None, "Role not found"

    if 'role_name' in data:
        new_name = data['role_name'].strip()
        if not new_name:
            return None, "role_name cannot be empty"
        if len(new_name) > 100:
            return None, "role_name must be 100 characters or fewer"
        if role.role_name == ADMIN_ROLE_NAME and new_name != ADMIN_ROLE_NAME:
            return None, "The Admin role name is protected and cannot be changed"

        existing = Role.query.filter(
            Role.role_name == new_name,
            Role.id != role_id
        ).first()
        if existing:
            return None, "Role name already exists"
        role.role_name = new_name

    try:
        db.session.commit()
        return role, None
    except IntegrityError:
        db.session.rollback()
        return None, "Role name already exists"
    except Exception as exc:
        db.session.rollback()
        return None, f"Update failed: {str(exc)}"


def delete_role(role_id: int) -> Tuple[bool, Optional[str]]:
    """Delete a role (cascades to role_permissions & user_roles)."""
    role = Role.query.get(role_id)
    if not role:
        return False, "Role not found"
    if role.role_name == ADMIN_ROLE_NAME:
        return False, "The Admin role is protected and cannot be deleted"

    try:
        db.session.delete(role)
        db.session.commit()
        return True, None
    except Exception as exc:
        db.session.rollback()
        return False, f"Delete failed: {str(exc)}"


# ---------------------------------------------------------------------------
# Role-Permission pivot
# ---------------------------------------------------------------------------

def get_permissions_for_role(role_id: int) -> Tuple[Optional[List[dict]], Optional[str]]:
    """List all permissions attached to a role."""
    role = Role.query.get(role_id)
    if not role:
        return None, "Role not found"

    permissions = [rp.permission.to_dict() for rp in role.role_permissions]
    return permissions, None


def assign_permission_to_role(
    role_id: int, permission_id: int
) -> Tuple[bool, Optional[str]]:
    """Assign a single permission to a role."""
    role = Role.query.get(role_id)
    if not role:
        return False, "Role not found"

    permission = Permission.query.get(permission_id)
    if not permission:
        return False, "Permission not found"

    existing = RolePermission.query.filter_by(
        role_id=role_id, permission_id=permission_id
    ).first()
    if existing:
        return False, "Permission already assigned to this role"

    try:
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        db.session.add(rp)
        db.session.commit()
        return True, None
    except IntegrityError:
        db.session.rollback()
        return False, "Permission already assigned to this role"
    except Exception as exc:
        db.session.rollback()
        return False, f"Assignment failed: {str(exc)}"


def assign_permissions_bulk(
    role_id: int, permission_ids: List[int]
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Assign multiple permissions to a role in one transaction.
    
    Returns a summary: { added: [...], skipped: [...], not_found: [...] }
    """
    role = Role.query.get(role_id)
    if not role:
        return None, "Role not found"

    added = []
    skipped = []
    not_found = []

    for pid in permission_ids:
        perm = Permission.query.get(pid)
        if not perm:
            not_found.append(pid)
            continue

        exists = RolePermission.query.filter_by(
            role_id=role_id, permission_id=pid
        ).first()
        if exists:
            skipped.append(pid)
            continue

        db.session.add(RolePermission(role_id=role_id, permission_id=pid))
        added.append(pid)

    try:
        db.session.commit()
        return {
            'added': added,
            'skipped': skipped,
            'not_found': not_found
        }, None
    except Exception as exc:
        db.session.rollback()
        return None, f"Bulk assignment failed: {str(exc)}"


def remove_permission_from_role(
    role_id: int, permission_id: int
) -> Tuple[bool, Optional[str]]:
    """Remove a single permission from a role."""
    rp = RolePermission.query.filter_by(
        role_id=role_id, permission_id=permission_id
    ).first()
    if not rp:
        return False, "Permission assignment not found"

    try:
        db.session.delete(rp)
        db.session.commit()
        return True, None
    except Exception as exc:
        db.session.rollback()
        return False, f"Removal failed: {str(exc)}"


def replace_permissions_for_role(
    role_id: int, permission_ids: List[int]
) -> Tuple[Optional[List[dict]], Optional[str]]:
    """
    Replace ALL permissions for a role with the provided list.
    Useful for a PUT-style "set these exact permissions" workflow.
    """
    role = Role.query.get(role_id)
    if not role:
        return None, "Role not found"

    # Validate all permission ids first
    valid_perms = []
    for pid in permission_ids:
        perm = Permission.query.get(pid)
        if not perm:
            return None, f"Permission id {pid} not found"
        valid_perms.append(perm)

    try:
        # Delete existing
        RolePermission.query.filter_by(role_id=role_id).delete()

        # Insert new set
        for perm in valid_perms:
            db.session.add(RolePermission(role_id=role_id, permission_id=perm.id))

        db.session.commit()
        return [p.to_dict() for p in valid_perms], None
    except Exception as exc:
        db.session.rollback()
        return None, f"Replace failed: {str(exc)}"


# ---------------------------------------------------------------------------
# User-Role pivot
# ---------------------------------------------------------------------------

def get_roles_for_user(user_id: int) -> Tuple[Optional[List[dict]], Optional[str]]:
    """List all roles assigned to a user."""
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    roles = [ur.role.to_dict() for ur in user.user_roles]
    return roles, None


def assign_role_to_user(
    user_id: int, role_id: int
) -> Tuple[bool, Optional[str]]:
    """Assign a role to a user."""
    user = User.query.get(user_id)
    if not user:
        return False, "User not found"

    role = Role.query.get(role_id)
    if not role:
        return False, "Role not found"

    existing = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if existing:
        return False, "Role already assigned to this user"

    try:
        db.session.add(UserRole(user_id=user_id, role_id=role_id))
        db.session.commit()
        return True, None
    except IntegrityError:
        db.session.rollback()
        return False, "Role already assigned to this user"
    except Exception as exc:
        db.session.rollback()
        return False, f"Assignment failed: {str(exc)}"


def assign_roles_bulk(
    user_id: int, role_ids: List[int]
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Assign multiple roles to a user in a single transaction."""
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    added = []
    skipped = []
    not_found = []

    for rid in role_ids:
        role = Role.query.get(rid)
        if not role:
            not_found.append(rid)
            continue

        exists = UserRole.query.filter_by(user_id=user_id, role_id=rid).first()
        if exists:
            skipped.append(rid)
            continue

        db.session.add(UserRole(user_id=user_id, role_id=rid))
        added.append(rid)

    try:
        db.session.commit()
        return {
            'added': added,
            'skipped': skipped,
            'not_found': not_found
        }, None
    except Exception as exc:
        db.session.rollback()
        return None, f"Bulk assignment failed: {str(exc)}"


def replace_roles_for_user(
    user_id: int, role_ids: List[int]
) -> Tuple[Optional[List[dict]], Optional[str]]:
    """
    Replace ALL roles assigned to a user with the provided set.

    The last Admin user cannot be stripped of the Admin role.
    """
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    normalized_role_ids = []
    seen_role_ids = set()
    for role_id in role_ids:
        try:
            normalized_role_id = int(role_id)
        except (TypeError, ValueError):
            return None, f"role_id '{role_id}' must be an integer"

        if normalized_role_id in seen_role_ids:
            continue

        seen_role_ids.add(normalized_role_id)
        normalized_role_ids.append(normalized_role_id)

    validated_roles = []
    for role_id in normalized_role_ids:
        role = Role.query.get(role_id)
        if not role:
            return None, f"Role id {role_id} not found"
        validated_roles.append(role)

    admin_role = get_role_by_name(ADMIN_ROLE_NAME)
    if admin_role and user.has_role(ADMIN_ROLE_NAME) and admin_role.id not in normalized_role_ids:
        admin_count = UserRole.query.filter_by(role_id=admin_role.id).count()
        if admin_count <= 1:
            return None, "Cannot remove the last admin user"

    try:
        UserRole.query.filter_by(user_id=user_id).delete()

        for role in validated_roles:
            db.session.add(UserRole(user_id=user_id, role_id=role.id))

        db.session.commit()
        return [role.to_dict() for role in validated_roles], None
    except Exception as exc:
        db.session.rollback()
        return None, f"Role replacement failed: {str(exc)}"


def remove_role_from_user(
    user_id: int, role_id: int
) -> Tuple[bool, Optional[str]]:
    """Remove a role from a user."""
    ur = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if not ur:
        return False, "Role assignment not found"

    role = Role.query.get(role_id)
    if role and role.role_name == ADMIN_ROLE_NAME:
        admin_count = UserRole.query.filter_by(role_id=role_id).count()
        if admin_count <= 1:
            return False, "Cannot remove the last admin user"

    try:
        db.session.delete(ur)
        db.session.commit()
        return True, None
    except Exception as exc:
        db.session.rollback()
        return False, f"Removal failed: {str(exc)}"


# ---------------------------------------------------------------------------
# Permission CRUD
# ---------------------------------------------------------------------------

def get_all_permissions(page: int, per_page: int):
    """Return paginated permissions."""
    query = Permission.query.order_by(Permission.id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination


def get_permission_by_id(permission_id: int) -> Optional[Permission]:
    """Return a single permission or None."""
    return Permission.query.get(permission_id)


def create_permission(permission_name: str) -> Tuple[Optional[Permission], Optional[str]]:
    """Create a new permission."""
    permission_name = permission_name.strip()
    if not permission_name:
        return None, "permission_name is required"

    if len(permission_name) > 150:
        return None, "permission_name must be 150 characters or fewer"

    # Validate format: should follow resource:action pattern
    if ':' not in permission_name:
        return None, "permission_name should follow 'resource:action' format (e.g. 'orders:read')"

    parts = permission_name.split(':')
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        return None, "permission_name should follow 'resource:action' format (e.g. 'orders:read')"

    if Permission.query.filter_by(permission_name=permission_name).first():
        return None, "Permission name already exists"

    try:
        perm = Permission(permission_name=permission_name)
        db.session.add(perm)
        db.session.commit()
        return perm, None
    except IntegrityError:
        db.session.rollback()
        return None, "Permission name already exists"
    except Exception as exc:
        db.session.rollback()
        return None, f"Permission creation failed: {str(exc)}"


def update_permission(
    permission_id: int, data: dict
) -> Tuple[Optional[Permission], Optional[str]]:
    """Update a permission."""
    perm = Permission.query.get(permission_id)
    if not perm:
        return None, "Permission not found"

    if 'permission_name' in data:
        new_name = data['permission_name'].strip()
        if not new_name:
            return None, "permission_name cannot be empty"
        if len(new_name) > 150:
            return None, "permission_name must be 150 characters or fewer"
        if ':' not in new_name:
            return None, "permission_name should follow 'resource:action' format (e.g. 'orders:read')"

        parts = new_name.split(':')
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            return None, "permission_name should follow 'resource:action' format (e.g. 'orders:read')"

        existing = Permission.query.filter(
            Permission.permission_name == new_name,
            Permission.id != permission_id
        ).first()
        if existing:
            return None, "Permission name already exists"
        perm.permission_name = new_name

    try:
        db.session.commit()
        return perm, None
    except IntegrityError:
        db.session.rollback()
        return None, "Permission name already exists"
    except Exception as exc:
        db.session.rollback()
        return None, f"Update failed: {str(exc)}"


def delete_permission(permission_id: int) -> Tuple[bool, Optional[str]]:
    """Delete a permission (cascades to role_permissions)."""
    perm = Permission.query.get(permission_id)
    if not perm:
        return False, "Permission not found"

    try:
        db.session.delete(perm)
        db.session.commit()
        return True, None
    except Exception as exc:
        db.session.rollback()
        return False, f"Delete failed: {str(exc)}"


def create_permissions_bulk(
    permission_names: List[str]
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Create multiple permissions in a single transaction."""
    created = []
    skipped = []
    errors_list = []

    for name in permission_names:
        name = name.strip()
        if not name:
            errors_list.append({'name': name, 'reason': 'Empty name'})
            continue

        if ':' not in name:
            errors_list.append({'name': name, 'reason': "Must follow 'resource:action' format"})
            continue

        if Permission.query.filter_by(permission_name=name).first():
            skipped.append(name)
            continue

        db.session.add(Permission(permission_name=name))
        created.append(name)

    try:
        db.session.commit()
        return {
            'created': created,
            'skipped': skipped,
            'errors': errors_list
        }, None
    except Exception as exc:
        db.session.rollback()
        return None, f"Bulk creation failed: {str(exc)}"


# ---------------------------------------------------------------------------
# Permission check helper (used by the permission_required decorator)
# ---------------------------------------------------------------------------

def user_has_permission(user_id: int, permission_name: str) -> bool:
    """
    Check whether a user holds a given permission through any of their roles.
    """
    permission = Permission.query.filter_by(permission_name=permission_name).first()
    if not permission:
        return False

    user_role_ids = [
        ur.role_id for ur in UserRole.query.filter_by(user_id=user_id).all()
    ]
    if not user_role_ids:
        return False

    return RolePermission.query.filter(
        RolePermission.role_id.in_(user_role_ids),
        RolePermission.permission_id == permission.id
    ).first() is not None
