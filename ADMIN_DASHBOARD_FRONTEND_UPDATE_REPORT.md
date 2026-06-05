# Admin Dashboard Frontend Update Report

## Purpose

The backend now supports a more professional admin dashboard for managing users, roles, and permissions. The frontend should add an access-management area where an admin can:

- View dashboard access-control stats.
- Search and filter users by role/admin status.
- Promote a user to admin.
- Assign or remove individual roles.
- Replace all roles for a user in one action.
- Create, update, and delete non-system roles.
- Assign different permissions to each role.
- View each user's effective permissions.

All endpoints below require a JWT token for a user who has the `Admin` role.

Authentication header:

```http
Authorization: Bearer <ADMIN_JWT_TOKEN>
```

## Backend Files Updated

- `app/routes/admin_routes.py`
- `app/services/role_service.py`
- `app/routes/role_routes.py`
- `app/routes/permission_routes.py`
- `app/routes/user_routes.py`

## Frontend Areas To Update

### 1. Admin Dashboard Overview

Use the existing admin dashboard page and add an "Access Control" summary section.

Endpoint:

```http
GET /api/admin/dashboard
```

New response data inside `data.access_control`:

```json
{
  "total_roles": 4,
  "total_permissions": 16,
  "total_admin_users": 2,
  "users_with_roles": 10,
  "role_breakdown": [
    {
      "role_name": "Admin",
      "users_count": 2
    }
  ],
  "recent_admins": []
}
```

Suggested UI:

- Add stat tiles for total roles, total permissions, admin users, and users with roles.
- Add a compact role breakdown table or horizontal bar list.
- Add a recent admins list using the returned `recent_admins` users.

### 2. User Management Table

Update the admin users table to show role and permission information.

Endpoint:

```http
GET /api/admin/users?page=1&per_page=20&search=&role_id=&is_admin=
```

New filters:

| Query | Type | Example | Purpose |
|---|---:|---|---|
| `role_id` | number | `role_id=3` | Show users with a specific role |
| `is_admin` | boolean string | `is_admin=true` | Show only admins or non-admins |

Each user item now includes:

```json
{
  "id": 1,
  "full_name": "Main Admin",
  "email": "admin@example.com",
  "is_active": true,
  "roles": [
    {
      "id": 1,
      "role_name": "Admin"
    }
  ],
  "is_admin": true,
  "effective_permissions": [
    {
      "id": 1,
      "permission_name": "users:read"
    }
  ],
  "effective_permission_names": ["users:read"],
  "roles_count": 1,
  "permissions_count": 1
}
```

Suggested UI:

- Show role chips in the users table.
- Show an "Admin" badge when `is_admin` is true.
- Add filters for "All users", "Admins", "Non-admins", and "Role".
- Add an "Access" action button that opens a side panel or modal.

### 3. User Access Drawer Or Page

Use this endpoint when opening a user's access-management view.

Endpoint:

```http
GET /api/admin/users/<user_id>/access
```

Response shape:

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "user": {},
    "available_roles": [],
    "available_permissions": []
  }
}
```

`available_roles` item:

```json
{
  "id": 1,
  "custom_id": "ROL-00001",
  "role_name": "Admin",
  "permissions": [],
  "permissions_count": 16,
  "users_count": 2,
  "is_system_role": true
}
```

`available_permissions` item:

```json
{
  "id": 1,
  "permission_name": "users:read",
  "resource": "users",
  "action": "read",
  "roles_count": 2
}
```

Suggested UI:

- User identity summary at the top.
- Role checklist using `available_roles`.
- Effective permissions list grouped by `resource`.
- Clear save button for replacing roles.
- Separate quick action for "Make admin".

### 4. Make Someone Admin

Use this for a one-click promote action.

Endpoint:

```http
POST /api/admin/users/<user_id>/make-admin
```

Body:

```json
{}
```

Success response:

```json
{
  "success": true,
  "message": "User is now an admin",
  "data": {
    "user": {},
    "admin_role": {
      "id": 1,
      "role_name": "Admin"
    }
  }
}
```

Frontend behavior:

- Disable the button if `user.is_admin` is already true.
- Refresh the user row or access drawer after success.
- Show the backend `message` in a toast.

### 5. Replace User Roles

Use this when the admin checks/unchecks roles and saves.

Endpoint:

```http
PUT /api/admin/users/<user_id>/roles
```

Body:

```json
{
  "role_ids": [1, 3, 4]
}
```

Success response:

```json
{
  "success": true,
  "message": "User roles updated successfully",
  "data": {
    "user": {},
    "roles": []
  }
}
```

Important error cases to handle:

```json
{
  "success": false,
  "message": "You cannot remove your own Admin role from the admin dashboard"
}
```

```json
{
  "success": false,
  "message": "Cannot remove the last admin user"
}
```

Frontend behavior:

- If editing the logged-in admin, keep the Admin role checked and disabled.
- Show a confirmation prompt before removing the Admin role from another user.
- Keep the current UI state if the backend rejects the update.

### 6. Assign Or Remove One Role

These are useful for quick row actions.

Assign role:

```http
POST /api/admin/users/<user_id>/roles
```

Body:

```json
{
  "role_id": 3
}
```

Remove role:

```http
DELETE /api/admin/users/<user_id>/roles/<role_id>
```

Suggested UI:

- Prefer the full role replacement flow in the access drawer.
- Use single assign/remove calls only for quick actions like "Add Manager" or "Remove Viewer".

### 7. Role Management Screen

Add or update a Roles screen under the admin dashboard.

List roles:

```http
GET /api/admin/roles
```

Create role:

```http
POST /api/admin/roles
```

Body:

```json
{
  "role_name": "Inventory Manager",
  "permission_ids": [1, 2, 5]
}
```

Update role name and permissions:

```http
PUT /api/admin/roles/<role_id>
```

Body:

```json
{
  "role_name": "Inventory Manager",
  "permission_ids": [1, 2, 5, 6]
}
```

Replace only role permissions:

```http
PUT /api/admin/roles/<role_id>/permissions
```

Body:

```json
{
  "permission_ids": [1, 2, 5, 6]
}
```

Delete role:

```http
DELETE /api/admin/roles/<role_id>
```

Frontend behavior:

- Do not show delete for roles where `is_system_role` is true.
- Do not allow renaming `Admin`.
- Show `users_count` before delete; if the role has users, warn that users will lose the role.
- Group permissions by `resource` and show checkboxes for each `action`.

### 8. Permission Picker

Use the admin permissions endpoint to build role permission checklists.

Endpoint:

```http
GET /api/admin/permissions
```

Response item:

```json
{
  "id": 1,
  "permission_name": "orders:read",
  "resource": "orders",
  "action": "read",
  "roles_count": 2
}
```

Suggested UI grouping:

| Resource | Actions |
|---|---|
| `users` | `create`, `read`, `write`, `delete` |
| `products` | `create`, `read`, `write`, `delete` |
| `orders` | `create`, `read`, `write`, `cancel` |
| `roles` | `manage` |
| `permissions` | `manage` |
| `reports` | `read` |
| `settings` | `manage` |

## Suggested Frontend Route Structure

Use whichever routing style exists in the frontend, but this is the recommended admin information architecture:

| Page | Purpose |
|---|---|
| `/admin/dashboard` | Overview stats, including access-control stats |
| `/admin/users` | User table, filters, role badges, access action |
| `/admin/users/:id/access` or drawer | User roles and effective permissions |
| `/admin/roles` | Role list, create/edit/delete roles |
| `/admin/roles/:id` or modal | Role permission editor |

## Suggested Components

| Component | Responsibility |
|---|---|
| `AdminAccessStats` | Render `data.access_control` from dashboard |
| `UserRoleBadges` | Show role chips and Admin badge |
| `UserAccessDrawer` | Load `/api/admin/users/<id>/access` and edit roles |
| `RoleChecklist` | Check/uncheck available roles for a user |
| `PermissionMatrix` | Group permissions by resource and action |
| `RoleEditorModal` | Create or update a role and its permissions |
| `ConfirmAdminRoleChange` | Confirm sensitive admin demotion/removal |

## API Helper Examples

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

function getAdminToken() {
  return localStorage.getItem('adminToken') || localStorage.getItem('token');
}

async function adminRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getAdminToken()}`,
      ...(options.headers || {})
    }
  });

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(result.message || result.error || 'Request failed');
  }

  return result.data;
}
```

```javascript
export function makeUserAdmin(userId) {
  return adminRequest(`/api/admin/users/${userId}/make-admin`, {
    method: 'POST',
    body: JSON.stringify({})
  });
}

export function replaceUserRoles(userId, roleIds) {
  return adminRequest(`/api/admin/users/${userId}/roles`, {
    method: 'PUT',
    body: JSON.stringify({ role_ids: roleIds })
  });
}

export function updateRolePermissions(roleId, permissionIds) {
  return adminRequest(`/api/admin/roles/${roleId}/permissions`, {
    method: 'PUT',
    body: JSON.stringify({ permission_ids: permissionIds })
  });
}
```

## UX And Safety Requirements

- Always show role changes before saving.
- Always confirm before removing the Admin role from a user.
- Disable self-removal of the Admin role in the UI.
- Do not allow delete/rename actions for `is_system_role: true`.
- Refresh user access data after every successful role change.
- Display backend error messages directly in a toast or inline alert.
- Treat permissions as inherited from roles. The user does not receive direct permissions.

## Acceptance Checklist

- Admin can see access-control stats on the dashboard.
- Admin can filter users by Admin status.
- Admin can open a user access drawer/page.
- Admin can make a user an admin.
- Admin can assign multiple roles to a user.
- Admin cannot remove their own Admin role.
- Admin can create a new role with permissions.
- Admin can update a role's permissions.
- Admin cannot delete or rename the Admin role.
- Effective permissions update after role changes.
- Frontend handles `400`, `403`, and `500` responses with useful messages.

## Backend Verification Already Completed

The backend changes were validated with:

- Python compile check for edited files.
- Flask route registration under testing config with Cloudinary stubbed.
- In-memory smoke test for:
  - Promoting a user to admin.
  - Blocking current admin self-demotion.
  - Updating role permissions.
  - Filtering users by `is_admin=true`.

