# TORIDA B2B Marketplace — API Documentation

> **Base URL**: `http://localhost:5000`  
> **Version**: 1.0.0  
> **Auth**: JWT Bearer Token (`Authorization: Bearer <token>`)

---

## Table of Contents

1. [Response Format](#response-format)
2. [Authentication](#1-authentication)
3. [Users](#2-users)
4. [Roles & Permissions](#3-roles--permissions)
5. [Governorates](#4-governorates)
6. [User Types](#5-user-types)
7. [Business Profiles](#6-business-profiles)
8. [Categories](#7-categories)
9. [Products](#8-products)
10. [Cart](#9-cart)
11. [Wishlist](#10-wishlist)
12. [Orders](#11-orders)
13. [Payments](#12-payments)
14. [Reviews](#13-reviews)
15. [Notifications](#14-notifications)
16. [Addresses](#15-addresses)

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Success",
  "data": { ... }
}
```

### Paginated Response
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_items": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Role name already exists",
  "message": "Role name already exists",
  "code": "ROLE_CREATE_FAILED"
}
```

### Validation Error (422)
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "field_name": ["Field Name is required"]
  }
}
```

---

## 1. Authentication

Base path: `/api/auth`

### POST `/api/auth/register`
Register a new user. **Public**.

**Body:**
```json
{
  "full_name": "Ahmed Hassan",
  "phone": "201234567890",
  "email": "ahmed@example.com",
  "password": "SecurePass1",
  "type_id": 2,
  "gov_id": 1
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `full_name` | string | ✅ | |
| `phone` | string | ✅ | Egyptian format |
| `email` | string | ✅ | Unique |
| `password` | string | ✅ | Min 8 chars, 1 upper, 1 lower, 1 digit |
| `type_id` | int | ✅ | 1=Supplier, 2=Retailer, 3=Company |
| `gov_id` | int | ✅ | Governorate ID |

**Response** `201`:
```json
{
  "success": true,
  "data": {
    "user": { "id": 1, "custom_id": "RET-1001", ... },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

---

### POST `/api/auth/login`
Login with email & password. **Public**.

**Body:**
```json
{
  "email": "ahmed@example.com",
  "password": "SecurePass1"
}
```

**Response** `200`: Returns `user`, `access_token`, `refresh_token`.

---

### POST `/api/auth/logout`
Logout (client discards tokens). **🔒 Auth Required**.

**Response** `200`: `{ "message": "Logged out successfully" }`

---

### POST `/api/auth/refresh`
Refresh access token. **Public**.

**Body:**
```json
{ "refresh_token": "eyJ..." }
```

**Response** `200`: Returns new `access_token` and `refresh_token`.

---

### POST `/api/auth/verify-email`
Verify email with OTP. **🔒 Auth Required**.

**Body:** `{ "otp": "123456" }`

---

### POST `/api/auth/resend-otp`
Resend verification OTP. **🔒 Auth Required**.

---

### POST `/api/auth/forgot-password`
Request password reset OTP. **Public**.

**Body:** `{ "email": "ahmed@example.com" }`

---

### POST `/api/auth/reset-password`
Reset password with OTP. **Public**.

**Body:**
```json
{
  "email": "ahmed@example.com",
  "otp": "123456",
  "new_password": "NewSecure1"
}
```

---

### POST `/api/auth/change-password`
Change password for logged-in user. **🔒 Auth Required**.

**Body:**
```json
{
  "current_password": "OldPass1",
  "new_password": "NewPass1"
}
```

---

### GET `/api/auth/me`
Get current authenticated user profile. **🔒 Auth Required**.

**Response** `200`: Full user object with roles and business profile.

---

## 2. Users

Base path: `/api/users` — **🔒 All endpoints require Auth**

### GET `/api/users`
List users with pagination and filters.

| Query Param | Type | Description |
|------------|------|-------------|
| `page` | int | Page number (default: 1) |
| `per_page` | int | Items per page (default: 20, max: 100) |
| `type_id` | int | Filter by user type |
| `gov_id` | int | Filter by governorate |
| `is_active` | string | `"true"` or `"false"` |
| `search` | string | Search name, email, phone |

---

### GET `/api/users/:user_id`
Get user by ID (includes roles & business profile).

---

### PUT `/api/users/:user_id`
Update user. Users can only update their own profile.

**Body** (all optional):
```json
{
  "full_name": "New Name",
  "email": "new@example.com",
  "phone": "201111111111",
  "gov_id": 2,
  "is_active": true
}
```

---

### DELETE `/api/users/:user_id`
Soft-delete (deactivate) user.

---

### GET `/api/users/:user_id/roles`
List roles assigned to user.

### POST `/api/users/:user_id/roles`
Assign role to user. **Body:** `{ "role_id": 1 }`

### DELETE `/api/users/:user_id/roles/:role_id`
Remove role from user.

---

### GET `/api/users/:user_id/addresses`
List user's addresses.

### GET `/api/users/:user_id/business-profile`
Get user's business profile.

---

## 3. Roles & Permissions

### 3.1 Roles

Base path: `/api/roles` — **🔒 All endpoints require Auth**

#### GET `/api/roles`
List roles (paginated). Query: `page`, `per_page`.

**Response item:**
```json
{
  "id": 1,
  "custom_id": "ROL-00001",
  "role_name": "Admin",
  "created_at": "2026-01-01T00:00:00"
}
```

#### GET `/api/roles/:role_id`
Get role with its permissions.

**Response:**
```json
{
  "id": 1,
  "custom_id": "ROL-00001",
  "role_name": "Admin",
  "created_at": "...",
  "permissions": [
    { "id": 1, "permission_name": "users:read" },
    { "id": 2, "permission_name": "users:write" }
  ]
}
```

#### POST `/api/roles`
Create role. The MySQL trigger auto-generates `custom_id` (ROL-XXXXX).

**Body:** `{ "role_name": "Moderator" }`

#### PUT `/api/roles/:role_id`
Update role name.

**Body:** `{ "role_name": "Super Admin" }`

#### DELETE `/api/roles/:role_id`
Delete role. Cascades to `role_permissions` and `user_roles`.

---

### 3.2 Role ↔ Permission Pivot

#### GET `/api/roles/:role_id/permissions`
List all permissions assigned to a role.

#### POST `/api/roles/:role_id/permissions`
Assign one permission. **Body:** `{ "permission_id": 5 }`

#### POST `/api/roles/:role_id/permissions/bulk`
Assign many permissions at once.

**Body:** `{ "permission_ids": [1, 2, 3, 4] }`

**Response:**
```json
{
  "data": {
    "added": [1, 2],
    "skipped": [3],
    "not_found": [4]
  }
}
```

#### PUT `/api/roles/:role_id/permissions`
Replace ALL permissions for a role (set-style).

**Body:** `{ "permission_ids": [1, 2, 3] }`

#### DELETE `/api/roles/:role_id/permissions/:permission_id`
Remove one permission from a role.

---

### 3.3 User ↔ Role Pivot (via roles path)

#### GET `/api/roles/users/:user_id`
List all roles for a user.

#### POST `/api/roles/users/:user_id`
Assign one role. **Body:** `{ "role_id": 1 }`

#### POST `/api/roles/users/:user_id/bulk`
Assign many roles. **Body:** `{ "role_ids": [1, 2, 3] }`

#### DELETE `/api/roles/users/:user_id/:role_id`
Remove role from user.

---

### 3.4 Permissions

Base path: `/api/permissions` — **🔒 All endpoints require Auth**

> Permission names must follow `resource:action` format (e.g. `orders:read`).

#### GET `/api/permissions`
List permissions (paginated). Query: `page`, `per_page`.

**Response item:**
```json
{ "id": 1, "permission_name": "orders:read" }
```

#### GET `/api/permissions/:permission_id`
Get single permission.

#### POST `/api/permissions`
Create permission. **Body:** `{ "permission_name": "invoices:read" }`

#### POST `/api/permissions/bulk`
Bulk create permissions.

**Body:**
```json
{ "permission_names": ["invoices:read", "invoices:write", "invoices:delete"] }
```

**Response:**
```json
{
  "data": {
    "created": ["invoices:read", "invoices:write"],
    "skipped": ["invoices:delete"],
    "errors": []
  }
}
```

#### PUT `/api/permissions/:permission_id`
Update permission. **Body:** `{ "permission_name": "invoices:manage" }`

#### DELETE `/api/permissions/:permission_id`
Delete permission (cascades to `role_permissions`).

---

## 4. Governorates

Base path: `/api/governorates`

### GET `/api/governorates`
List all governorates. **Public**.

### GET `/api/governorates/:id`
Get governorate by ID. **Public**.

### POST `/api/governorates`
Create governorate. **🔒 Auth**. Body: `{ "gov_name": "New Gov" }`

### PUT `/api/governorates/:id`
Update governorate. **🔒 Auth**. Body: `{ "gov_name": "Updated" }`

### DELETE `/api/governorates/:id`
Delete governorate (fails if users exist). **🔒 Auth**.

---

## 5. User Types

Base path: `/api/user-types`

### GET `/api/user-types`
List all user types. **Public**.

**Response:**
```json
[
  { "id": 1, "type_name": "Supplier", "can_sell": true, "can_buy": false },
  { "id": 2, "type_name": "Retailer", "can_sell": false, "can_buy": true },
  { "id": 3, "type_name": "Company", "can_sell": true, "can_buy": false }
]
```

### GET `/api/user-types/:id`
Get user type by ID. **Public**.

### POST `/api/user-types`
Create user type. **🔒 Auth**.

**Body:** `{ "type_name": "Distributor", "can_sell": true, "can_buy": true }`

### PUT `/api/user-types/:id`
Update user type. **🔒 Auth**.

### DELETE `/api/user-types/:id`
Delete user type (fails if users exist). **🔒 Auth**.

---

## 6. Business Profiles

Base path: `/api/business-profiles` — **🔒 All endpoints require Auth**

### GET `/api/business-profiles`
List all business profiles (paginated).

### GET `/api/business-profiles/:user_id`
Get business profile by user ID.

### POST `/api/business-profiles`
Create business profile.

**Body:**
```json
{
  "business_name": "Tech Corp",
  "address": "123 Main St, Cairo",
  "tax_number": "TAX-12345",
  "commercial_register": "CR-67890"
}
```

### PUT `/api/business-profiles/:user_id`
Update business profile. Owner only.

### DELETE `/api/business-profiles/:user_id`
Delete business profile. Owner only.

---

## 7. Categories

Base path: `/api/categories`

### GET `/api/categories`
List all categories. **Public**. Query: `include_count=true` for product counts.

### GET `/api/categories/:id`
Get category with product count. **Public**.

### POST `/api/categories`
Create category. **🔒 Auth**. Body: `{ "category_name": "Electronics" }`

### PUT `/api/categories/:id`
Update category. **🔒 Auth**. Body: `{ "category_name": "Updated Name" }`

### DELETE `/api/categories/:id`
Delete category (fails if products exist). **🔒 Auth**.

---

## 8. Products

Base path: `/api/products`

### GET `/api/products`
List products (paginated, filtered). **Public** (active only by default).

| Query Param | Type | Description |
|------------|------|-------------|
| `page`, `per_page` | int | Pagination |
| `category_id` | int | Filter by category |
| `company_id` | int | Filter by seller |
| `min_price`, `max_price` | float | Price range |
| `is_active` | string | `"true"` / `"false"` |
| `search` | string | Search name & description |
| `sort_by` | string | Column name (default: `created_at`) |
| `sort_order` | string | `asc` or `desc` |

### GET `/api/products/:id`
Get product with reviews. **Public**.

### POST `/api/products`
Create product. **🔒 Auth** (Suppliers & Companies only).

**Body:**
```json
{
  "category_id": 1,
  "product_name": "Widget Pro",
  "description": "High-quality widget",
  "price": 29.99,
  "stock_quantity": 100,
  "is_active": true
}
```

### PUT `/api/products/:id`
Update product. **🔒 Auth** (Owner only).

### DELETE `/api/products/:id`
Delete product. **🔒 Auth** (Owner only).

### GET `/api/products/my-products`
Get current user's products (paginated). **🔒 Auth**.

---

### Product Images

#### GET `/api/products/:id/images`
List product images. **Public**.

#### POST `/api/products/:id/images`
Upload image. **🔒 Auth** (Owner). **Form-data**: `image` (file), `is_primary` (bool).

#### DELETE `/api/products/:product_id/images/:image_id`
Delete image. **🔒 Auth** (Owner).

#### POST `/api/products/:product_id/images/:image_id/set-primary`
Set image as primary. **🔒 Auth** (Owner).

---

## 9. Cart

Base path: `/api/cart` — **🔒 All endpoints require Auth**

### GET `/api/cart`
Get current user's cart with items and totals.

### POST `/api/cart/items`
Add item to cart.

**Body:** `{ "product_id": 1, "quantity": 2 }`

### PUT `/api/cart/items/:item_id`
Update cart item quantity. **Body:** `{ "quantity": 5 }`

### DELETE `/api/cart/items/:item_id`
Remove item from cart.

### DELETE `/api/cart`
Clear entire cart.

---

## 10. Wishlist

Base path: `/api/wishlist` — **🔒 All endpoints require Auth**

### GET `/api/wishlist`
Get wishlist (paginated).

### POST `/api/wishlist`
Add product. **Body:** `{ "product_id": 1 }`

### DELETE `/api/wishlist/:product_id`
Remove product from wishlist.

### GET `/api/wishlist/check/:product_id`
Check if product is in wishlist. Returns `{ "in_wishlist": true }`.

---

## 11. Orders

Base path: `/api/orders` — **🔒 All endpoints require Auth**

### GET `/api/orders`
List orders for current user (paginated). Buyers see their orders, sellers see orders for their products.

Query: `page`, `per_page`, `status`.

### GET `/api/orders/:id`
Get order with status history. Buyer or seller only.

### POST `/api/orders`
Create order from cart. **Retailers only**.

**Body (optional):** `{ "address_id": 1 }`

Creates one order per seller. Validates stock, reduces quantities, clears cart.

**Order status flow**: `pending` → `confirmed` → `processing` → `shipped` → `out_for_delivery` → `delivered`  
**Cancel**: allowed from `pending` or `confirmed`

### PUT `/api/orders/:id/status`
Update order status. Seller updates forward statuses; both can cancel.

**Body:** `{ "status": "confirmed", "note": "Optional note" }`

### POST `/api/orders/:id/cancel`
Cancel order. Restores stock.

### GET `/api/orders/:id/items`
List order items.

### GET `/api/orders/:id/history`
Get status change history.

---

## 12. Payments

Base path: `/api/payments` — **🔒 All endpoints require Auth**

### GET `/api/payments/order/:order_id`
Get payment for an order. Buyer or seller.

### POST `/api/payments`
Create payment record for an order. **Buyer only**.

**Body:** `{ "order_id": 1, "method": "cash_on_delivery" }`

### POST `/api/payments/:payment_id/pay`
Process payment (simulated). **Buyer only**.

**Body (optional):** `{ "transaction_id": "TXN-..." }`

### POST `/api/payments/:payment_id/refund`
Refund payment. **Seller only**. Only paid payments can be refunded.

---

## 13. Reviews

Base path: `/api/reviews`

### GET `/api/reviews/product/:product_id`
Get reviews for a product (paginated). **Public**.

### POST `/api/reviews`
Create a review. **🔒 Auth**. One review per user per product.

**Body:**
```json
{ "product_id": 1, "rating": 5, "comment": "Excellent quality!" }
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `product_id` | int | ✅ | |
| `rating` | int | ✅ | 1–5 |
| `comment` | string | ❌ | |

### PUT `/api/reviews/:id`
Update review. **🔒 Auth** (Author only).

### DELETE `/api/reviews/:id`
Delete review. **🔒 Auth** (Author only).

### GET `/api/reviews/my-reviews`
Get current user's reviews (paginated). **🔒 Auth**.

---

## 14. Notifications

Base path: `/api/notifications` — **🔒 All endpoints require Auth**

### GET `/api/notifications`
List notifications (paginated). Query: `is_read` (`"true"` / `"false"`).

### GET `/api/notifications/unread-count`
Get unread notification count. Returns `{ "unread_count": 5 }`.

### GET `/api/notifications/:id`
Get single notification.

### POST `/api/notifications/:id/read`
Mark notification as read.

### POST `/api/notifications/read-all`
Mark all notifications as read.

### DELETE `/api/notifications/:id`
Delete notification.

---

## 15. Addresses

Base path: `/api/addresses` — **🔒 All endpoints require Auth**

### GET `/api/addresses`
List current user's addresses (default first).

### GET `/api/addresses/:id`
Get address by ID. Owner only.

### POST `/api/addresses`
Create address. First address auto-becomes default.

**Body:**
```json
{
  "label": "Home",
  "full_address": "123 Main St, Apt 4",
  "gov_id": 1,
  "city": "Cairo",
  "postal_code": "11511",
  "is_default": true
}
```

| Field | Type | Required |
|-------|------|----------|
| `label` | string | ✅ |
| `full_address` | string | ✅ |
| `gov_id` | int | ✅ |
| `city` | string | ❌ |
| `postal_code` | string | ❌ |
| `is_default` | bool | ❌ |

### PUT `/api/addresses/:id`
Update address. Owner only.

### POST `/api/addresses/:id/set-default`
Set as default address. Owner only.

### DELETE `/api/addresses/:id`
Delete address. Owner only. If deleted was default, next address becomes default.

---

## Appendix: Error Codes

| Code | Description |
|------|-------------|
| `MISSING_BODY` | Request body is empty |
| `MISSING_FIELD` | Required field missing |
| `INVALID_FIELD` | Field has wrong type/format |
| `EMPTY_ARRAY` | Array field is empty |
| `ROLE_CREATE_FAILED` | Role creation error |
| `ROLE_UPDATE_FAILED` | Role update error |
| `ROLE_DELETE_FAILED` | Role deletion error |
| `ROLE_ASSIGN_FAILED` | Role assignment error |
| `ROLE_BULK_FAILED` | Bulk role assignment error |
| `ROLE_REMOVE_FAILED` | Role removal error |
| `PERM_CREATE_FAILED` | Permission creation error |
| `PERM_UPDATE_FAILED` | Permission update error |
| `PERM_DELETE_FAILED` | Permission deletion error |
| `PERM_ASSIGN_FAILED` | Permission assignment error |
| `PERM_BULK_FAILED` | Bulk permission error |
| `PERM_REPLACE_FAILED` | Permission replace error |
| `PERM_REMOVE_FAILED` | Permission removal error |
| `PERMISSION_DENIED` | User lacks required permission |

---

## Appendix: Seeded Data

### User Types
| ID | Name | Can Sell | Can Buy |
|----|------|----------|---------|
| 1 | Supplier | ✅ | ❌ |
| 2 | Retailer | ❌ | ✅ |
| 3 | Company | ✅ | ❌ |

### Default Roles
`Admin`, `Manager`, `Editor`, `Viewer`

### Default Permissions
`users:create`, `users:read`, `users:write`, `users:delete`, `products:create`, `products:read`, `products:write`, `products:delete`, `orders:create`, `orders:read`, `orders:write`, `orders:cancel`, `roles:manage`, `permissions:manage`, `reports:read`, `settings:manage`

### Governorates (27)
Cairo, Giza, Alexandria, Qalyubia, Port Said, Suez, Dakahlia, Sharqia, Gharbia, Kafr El Sheikh, Monufia, Beheira, Ismailia, Beni Suef, Fayoum, Minya, Assiut, Sohag, Qena, Luxor, Aswan, Red Sea, New Valley, Matrouh, North Sinai, South Sinai, Damietta
