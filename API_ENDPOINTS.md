# TORIDA API Endpoints Documentation
# Base URL: https://torida-v2.vercel.app

## Root & Health Check Endpoints

### Public Endpoints (No Authentication Required)

```
GET https://torida-v2.vercel.app/
Response: {"name": "TORIDA API", "message": "API running successfully", "version": "1.0.0"}

GET https://torida-v2.vercel.app/health
Response: {"status": "healthy", "service": "TORIDA API", "version": "1.0.0"}

GET https://torida-v2.vercel.app/api
Response: {API information and endpoints list}
```

---

## Authentication Endpoints
**Base Path:** `/api/auth`

### Public (No Token Required)
```
POST   https://torida-v2.vercel.app/api/auth/register
       Request body: {full_name, phone, email, password, type_id, gov_id}
       
POST   https://torida-v2.vercel.app/api/auth/login
       Request body: {email, password}
       
POST   https://torida-v2.vercel.app/api/auth/refresh-token
       Request body: {refresh_token}
       
POST   https://torida-v2.vercel.app/api/auth/verify-otp
       Request body: {email, otp}
       
POST   https://torida-v2.vercel.app/api/auth/resend-otp
       Request body: {email}
       
POST   https://torida-v2.vercel.app/api/auth/forgot-password
       Request body: {email}
       
POST   https://torida-v2.vercel.app/api/auth/reset-password
       Request body: {token, new_password}
       
POST   https://torida-v2.vercel.app/api/auth/logout
```

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/auth/me
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/auth/change-password
       Headers: Authorization: Bearer <token>
       Request body: {old_password, new_password}
```

---

## User Management Endpoints
**Base Path:** `/api/users`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/users
       Headers: Authorization: Bearer <token>
       Query params: page=1, per_page=20, type_id=, gov_id=, is_active=, search=
       
GET    https://torida-v2.vercel.app/api/users/<user_id>
       Headers: Authorization: Bearer <token>
       
PUT    https://torida-v2.vercel.app/api/users/<user_id>
       Headers: Authorization: Bearer <token>
       Request body: {full_name, phone, profile_picture, bio, ...}
       
DELETE https://torida-v2.vercel.app/api/users/<user_id>
       Headers: Authorization: Bearer <token>
       
GET    https://torida-v2.vercel.app/api/users/<user_id>/roles
       Headers: Authorization: Bearer <token>
```

---

## Role Management Endpoints
**Base Path:** `/api/roles`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/roles
       Headers: Authorization: Bearer <token>
       Query params: page=1, per_page=20, search=
       
GET    https://torida-v2.vercel.app/api/roles/<role_id>
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/roles
       Headers: Authorization: Bearer <token>
       Request body: {role_name, description}
       
PUT    https://torida-v2.vercel.app/api/roles/<role_id>
       Headers: Authorization: Bearer <token>
       Request body: {role_name, description}
       
DELETE https://torida-v2.vercel.app/api/roles/<role_id>
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/roles/<role_id>/permissions
       Headers: Authorization: Bearer <token>
       Request body: {permission_ids: []}
       
GET    https://torida-v2.vercel.app/api/roles/<role_id>/permissions
       Headers: Authorization: Bearer <token>
```

---

## Permission Endpoints
**Base Path:** `/api/permissions`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/permissions
       Headers: Authorization: Bearer <token>
       Query params: page=1, per_page=20, search=
       
GET    https://torida-v2.vercel.app/api/permissions/<permission_id>
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/permissions
       Headers: Authorization: Bearer <token>
       Request body: {permission_name, description}
       
PUT    https://torida-v2.vercel.app/api/permissions/<permission_id>
       Headers: Authorization: Bearer <token>
       Request body: {permission_name, description}
       
DELETE https://torida-v2.vercel.app/api/permissions/<permission_id>
       Headers: Authorization: Bearer <token>
```

---

## Governorate Endpoints
**Base Path:** `/api/governorates`

### Public (No Authentication Required)
```
GET    https://torida-v2.vercel.app/api/governorates
       Query params: page=1, per_page=50, search=
       
GET    https://torida-v2.vercel.app/api/governorates/<gov_id>
```

### Protected (Token Required)
```
POST   https://torida-v2.vercel.app/api/governorates
       Headers: Authorization: Bearer <token>
       Request body: {gov_name}
       
PUT    https://torida-v2.vercel.app/api/governorates/<gov_id>
       Headers: Authorization: Bearer <token>
       Request body: {gov_name}
       
DELETE https://torida-v2.vercel.app/api/governorates/<gov_id>
       Headers: Authorization: Bearer <token>
```

---

## User Type Endpoints
**Base Path:** `/api/user-types`

### Public (No Authentication Required)
```
GET    https://torida-v2.vercel.app/api/user-types
       Query params: page=1, per_page=20
       
GET    https://torida-v2.vercel.app/api/user-types/<type_id>
```

### Protected (Token Required)
```
POST   https://torida-v2.vercel.app/api/user-types
       Headers: Authorization: Bearer <token>
       Request body: {type_name, can_sell, can_buy}
       
PUT    https://torida-v2.vercel.app/api/user-types/<type_id>
       Headers: Authorization: Bearer <token>
       Request body: {type_name, can_sell, can_buy}
       
DELETE https://torida-v2.vercel.app/api/user-types/<type_id>
       Headers: Authorization: Bearer <token>
```

---

## Business Profile Endpoints
**Base Path:** `/api/business-profiles`

### Public (No Authentication Required)
```
GET    https://torida-v2.vercel.app/api/business-profiles
       Query params: page=1, per_page=20, type=, gov_id=, search=
       
GET    https://torida-v2.vercel.app/api/business-profiles/<profile_id>
```

### Protected (Token Required)
```
POST   https://torida-v2.vercel.app/api/business-profiles
       Headers: Authorization: Bearer <token>
       Request body: {business_name, business_type, tax_id, ...}
       
PUT    https://torida-v2.vercel.app/api/business-profiles/<profile_id>
       Headers: Authorization: Bearer <token>
       Request body: {business_name, business_type, ...}
       
DELETE https://torida-v2.vercel.app/api/business-profiles/<profile_id>
       Headers: Authorization: Bearer <token>
```

---

## Category Endpoints
**Base Path:** `/api/categories`

### Public (No Authentication Required)
```
GET    https://torida-v2.vercel.app/api/categories
       Query params: page=1, per_page=20, parent_id=, search=
       
GET    https://torida-v2.vercel.app/api/categories/<category_id>
```

### Protected (Token Required)
```
POST   https://torida-v2.vercel.app/api/categories
       Headers: Authorization: Bearer <token>
       Request body: {category_name, description, parent_id}
       
PUT    https://torida-v2.vercel.app/api/categories/<category_id>
       Headers: Authorization: Bearer <token>
       Request body: {category_name, description, parent_id}
       
DELETE https://torida-v2.vercel.app/api/categories/<category_id>
       Headers: Authorization: Bearer <token>
```

---

## Product Endpoints
**Base Path:** `/api/products`

### Public (No Authentication Required)
```
GET    https://torida-v2.vercel.app/api/products
       Query params: page=1, per_page=20, category_id=, company_id=, 
                     min_price=, max_price=, is_active=, search=, 
                     sort_by=, sort_order=
       
GET    https://torida-v2.vercel.app/api/products/<product_id>
```

### Protected (Token Required - Seller Only)
```
POST   https://torida-v2.vercel.app/api/products
       Headers: Authorization: Bearer <token>
       Request body: {product_name, description, category_id, price, 
                      quantity, unit, ...}
       Multipart: product_images (file upload)
       
PUT    https://torida-v2.vercel.app/api/products/<product_id>
       Headers: Authorization: Bearer <token>
       Request body: {product_name, description, price, quantity, ...}
       
DELETE https://torida-v2.vercel.app/api/products/<product_id>
       Headers: Authorization: Bearer <token>
```

---

## Product Images Endpoints
**Base Path:** `/api/products/<product_id>/images`

### Protected (Token Required - Seller Only)
```
POST   https://torida-v2.vercel.app/api/products/<product_id>/images
       Headers: Authorization: Bearer <token>
       Multipart: image (file upload)
       
DELETE https://torida-v2.vercel.app/api/products/<product_id>/images/<image_id>
       Headers: Authorization: Bearer <token>
```

---

## Cart Endpoints
**Base Path:** `/api/cart`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/cart
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/cart/items
       Headers: Authorization: Bearer <token>
       Request body: {product_id, quantity, unit}
       
PUT    https://torida-v2.vercel.app/api/cart/items/<item_id>
       Headers: Authorization: Bearer <token>
       Request body: {quantity}
       
DELETE https://torida-v2.vercel.app/api/cart/items/<item_id>
       Headers: Authorization: Bearer <token>
       
DELETE https://torida-v2.vercel.app/api/cart/clear
       Headers: Authorization: Bearer <token>
```

---

## Wishlist Endpoints
**Base Path:** `/api/wishlist`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/wishlist
       Headers: Authorization: Bearer <token>
       Query params: page=1, per_page=20
       
POST   https://torida-v2.vercel.app/api/wishlist
       Headers: Authorization: Bearer <token>
       Request body: {product_id}
       
DELETE https://torida-v2.vercel.app/api/wishlist/<product_id>
       Headers: Authorization: Bearer <token>
```

---

## Order Endpoints
**Base Path:** `/api/orders`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/orders
       Headers: Authorization: Bearer <token>
       Query params: page=1, per_page=20, status=, search=
       
GET    https://torida-v2.vercel.app/api/orders/<order_id>
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/orders
       Headers: Authorization: Bearer <token>
       Request body: {items, delivery_address_id, notes}
       
PUT    https://torida-v2.vercel.app/api/orders/<order_id>
       Headers: Authorization: Bearer <token>
       Request body: {status, notes}
       
DELETE https://torida-v2.vercel.app/api/orders/<order_id>
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/orders/<order_id>/cancel
       Headers: Authorization: Bearer <token>
       
GET    https://torida-v2.vercel.app/api/orders/<order_id>/history
       Headers: Authorization: Bearer <token>
```

---

## Payment Endpoints
**Base Path:** `/api/payments`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/payments
       Headers: Authorization: Bearer <token>
       Query params: page=1, per_page=20, status=, order_id=
       
GET    https://torida-v2.vercel.app/api/payments/<payment_id>
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/payments
       Headers: Authorization: Bearer <token>
       Request body: {order_id, payment_method, amount}
       
PUT    https://torida-v2.vercel.app/api/payments/<payment_id>
       Headers: Authorization: Bearer <token>
       Request body: {status}
```

---

## Product Review Endpoints
**Base Path:** `/api/reviews`

### Public (No Authentication Required)
```
GET    https://torida-v2.vercel.app/api/reviews
       Query params: page=1, per_page=20, product_id=, user_id=, min_rating=
       
GET    https://torida-v2.vercel.app/api/reviews/<review_id>
```

### Protected (Token Required)
```
POST   https://torida-v2.vercel.app/api/reviews
       Headers: Authorization: Bearer <token>
       Request body: {product_id, rating, comment}
       
PUT    https://torida-v2.vercel.app/api/reviews/<review_id>
       Headers: Authorization: Bearer <token>
       Request body: {rating, comment}
       
DELETE https://torida-v2.vercel.app/api/reviews/<review_id>
       Headers: Authorization: Bearer <token>
```

---

## Notification Endpoints
**Base Path:** `/api/notifications`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/notifications
       Headers: Authorization: Bearer <token>
       Query params: page=1, per_page=20, is_read=
       
GET    https://torida-v2.vercel.app/api/notifications/<notification_id>
       Headers: Authorization: Bearer <token>
       
PUT    https://torida-v2.vercel.app/api/notifications/<notification_id>
       Headers: Authorization: Bearer <token>
       Request body: {is_read}
       
PUT    https://torida-v2.vercel.app/api/notifications/mark-all-read
       Headers: Authorization: Bearer <token>
       
DELETE https://torida-v2.vercel.app/api/notifications/<notification_id>
       Headers: Authorization: Bearer <token>
```

---

## Address Endpoints
**Base Path:** `/api/addresses`

### Protected (Token Required)
```
GET    https://torida-v2.vercel.app/api/addresses
       Headers: Authorization: Bearer <token>
       Query params: page=1, per_page=20
       
GET    https://torida-v2.vercel.app/api/addresses/<address_id>
       Headers: Authorization: Bearer <token>
       
POST   https://torida-v2.vercel.app/api/addresses
       Headers: Authorization: Bearer <token>
       Request body: {gov_id, city, street, postal_code, is_default}
       
PUT    https://torida-v2.vercel.app/api/addresses/<address_id>
       Headers: Authorization: Bearer <token>
       Request body: {gov_id, city, street, postal_code, is_default}
       
DELETE https://torida-v2.vercel.app/api/addresses/<address_id>
       Headers: Authorization: Bearer <token>
```

---

## Upload/File Endpoints
**Base Path:** `/uploads`

### Public (No Authentication Required)
```
GET    https://torida-v2.vercel.app/uploads/<path:filename>
       Serve uploaded files (images, documents, etc.)
```

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    "id": 1,
    "name": "Example",
    ...
  }
}
```

### Paginated Response
```json
{
  "success": true,
  "message": "Retrieved successfully",
  "data": [
    {...},
    {...}
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "data": null
}
```

---

## HTTP Status Codes
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `500` - Internal Server Error

---

## Authentication
All protected endpoints require the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

Get token by logging in at:
```
POST https://torida-v2.vercel.app/api/auth/login
```

---

## Query Pagination Parameters
Most list endpoints support:
- `page` (default: 1)
- `per_page` (default: 20, max: 100)
- `search` (optional search term)

Example:
```
https://torida-v2.vercel.app/api/products?page=2&per_page=50&search=laptop
```

---

## File Uploads
For endpoints that support file uploads (products, images):
- Use `multipart/form-data` Content-Type
- Field name: `product_images` or `image`
- Allowed extensions: png, jpg, jpeg, gif, webp
- Max file size: 16MB

---

## Rate Limiting
Currently no rate limiting. Future implementations may include:
- Request throttling
- API key requirements
- Usage quotas

---

## API Version
Current version: **1.0.0**

Last updated: May 9, 2026
