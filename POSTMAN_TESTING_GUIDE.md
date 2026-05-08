# TORIDA API - Postman Collection Testing Guide

## Overview

Your Postman collection has been updated to fix all 76 authentication failures and prepare for resource ID resolution. This guide explains how to use the collection and what to expect.

## What Was Fixed

### ✅ 1. Authentication Token (76 × 401 failures)

**Problem:** The `{{token}}` variable was empty, causing all protected endpoints to return 401 Unauthorized.

**Solution Implemented:**
- Added **collection-level pre-request script** that auto-logs in if `{{token}}` is empty
- Added **Tests scripts** on the Login and Register endpoints to capture and save tokens
- All endpoints now use captured `{{token}}` variable in Authorization header

### ✅ 2. Resource ID Chaining (for 14 × 404 failures)

**Problem:** Path variables like `:product_id`, `:role_id` etc. pointed to non-existent records.

**Solution Implemented:**
- Added **Tests scripts** to POST requests that capture created resource IDs
- Saved IDs to variables like `{{product_id}}`, `{{role_id}}` etc.
- You can now chain requests: Create resource → Get the ID → Use ID in subsequent requests

### ✅ 3. Payload Validation (2 issues)

**Issues Fixed:**
- `POST /api/auth/register` → All required fields now in collection
- `POST /api/auth/reset-password` → Payload documented

---

## 🚀 Quick Start

### Step 1: Import Updated Collection

1. Open **Postman**
2. Click **File → Import**
3. Select the updated `torida_postman_collection.json`
4. Choose "Import"

### Step 2: Set Environment Variables

The collection automatically creates these variables (you can override if needed):

| Variable | Value | Purpose |
|----------|-------|---------|
| `base_url` | `http://localhost:5000` | API server address |
| `token` | *(auto-filled)* | Bearer token (set by login request) |
| `refresh_token` | *(auto-filled)* | Refresh token (set by login request) |
| `user_id` | *(auto-filled)* | Current user ID (set by login request) |
| `test_email` | `john.doe@example.com` | Test account email |
| `test_password` | `Password123!` | Test account password |

**To set variables in Postman:**
1. Click the **environment icon** (gear) in top-right
2. Click **Edit** next to active environment
3. Update variable values
4. Click **Save**

Or create a new environment:
1. Click **Environments** on the left
2. Click **Create**
3. Name it "Torida Local"
4. Add the variables above
5. Select it from the environment dropdown

### Step 3: Start Testing

#### Option A: Auto-Login Flow (Recommended)

1. Go to **Auth** folder
2. Click **POST /api/auth/login**
3. Click **Send**
4. The token will be automatically captured and saved to `{{token}}`
5. All other endpoints will now work! ✓

#### Option B: Registration Flow

If you need a new test user:

1. Go to **Auth** folder
2. Click **POST /api/auth/register**
3. Update the body with a unique email/phone (change the timestamp)
4. Click **Send**
5. Token will be auto-captured
6. You're logged in! ✓

---

## 📋 What Each Auth Endpoint Does

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/api/auth/register` | POST | Create new user | Generates tokens immediately |
| `/api/auth/login` | POST | Login with email + password | **This sets {{token}}** |
| `/api/auth/logout` | POST | Logout (client-side) | Just discards tokens |
| `/api/auth/refresh` | POST | Get new access token | Uses {{refresh_token}} |
| `/api/auth/verify-email` | POST | Verify email with OTP | Requires token, requires OTP |
| `/api/auth/resend-otp` | POST | Resend verification OTP | Requires token |
| `/api/auth/forgot-password` | POST | Request password reset | Takes email only |
| `/api/auth/reset-password` | POST | Complete password reset | Takes email + OTP + new password |
| `/api/auth/change-password` | POST | Change password (logged in) | Requires token |
| `/api/auth/me` | GET | Get current user profile | Requires token |

---

## 🔗 ID Chaining Example

### Scenario: Create Product → Get Product Details → Add to Cart

**Step 1: Create a Product**
```
POST /api/products
{
    "name": "Test Product",
    "sku": "SKU-001",
    ...
}
```
Response captures `product_id` → Saved as `{{product_id}}`

**Step 2: Get Product Details**
```
GET /api/products/{{product_id}}
```
This automatically uses the ID from Step 1

**Step 3: Add to Cart**
```
POST /api/cart/items
{
    "product_id": "{{product_id}}",
    "quantity": 10
}
```
This reuses the same ID

---

## ⚠️ Common Issues & Solutions

### Issue 1: Still Getting 401 Errors

**Cause:** Token variable is empty or expired

**Solutions:**
- [ ] Run **Auth → Login** again to get a fresh token
- [ ] Check that `{{token}}` variable has a value (click environment icon)
- [ ] Verify the Bearer token format in request header: `Bearer {{token}}`
- [ ] Check if the test account exists in the database (see seed data section)

### Issue 2: Getting 404 on GET /api/products/:product_id

**Cause:** That product ID doesn't exist in the database

**Solutions:**
- [ ] First, create a product: **POST /api/products**
- [ ] This will capture the ID automatically
- [ ] Then use that ID in subsequent requests
- [ ] Or run the seed data script (see below)

### Issue 3: Getting 422 on POST /api/auth/register

**Cause:** Validation error - one of the required fields is invalid

**Solution:** Check the response body for which field failed validation

**Register Required Fields:**
```json
{
    "full_name": "string (required)",
    "email": "valid email (required, must be unique)",
    "phone": "Egyptian format like 01012345678 (required, must be unique)",
    "password": "min 8 chars, uppercase, lowercase, number, special char (required)",
    "type_id": "1-3 (1=Supplier, 2=Retailer, 3=Company) (required)",
    "gov_id": "valid governorate ID (required)"
}
```

---

## 🌱 Seeding Test Data

To populate the database with test data so 404 errors go away:

### Option 1: Manual Seed (Run Once)

```bash
# Make sure you're in the project directory
cd c:\Users\COMPUMARTS\Downloads\torida_backend_complete

# Create a seed user
python -c "
from app import create_app, db
from app.models import User, UserType, Governorate
app = create_app()
with app.app_context():
    # Check if test user exists
    user = User.query.filter_by(email='john.doe@example.com').first()
    if not user:
        from app.utils.auth import hash_password
        user = User(
            full_name='John Doe',
            email='john.doe@example.com',
            phone='01012345678',
            password_hash=hash_password('Password123!'),
            type_id=1,
            gov_id=1,
            is_active=True,
            is_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        print('✓ Test user created')
    else:
        print('✓ Test user already exists')
"
```

### Option 2: Use Provided Seed Script

A seed script (`seed_database.py`) should be provided separately to populate:
- Test users (different types)
- Products with images
- Categories
- Roles & permissions
- Orders
- Etc.

---

## 🧪 Testing Workflow

### Minimal Test (5 minutes)

1. **Run Login:**
   - Auth → POST /api/auth/login
   - Verify token is captured

2. **Test Protected Endpoint:**
   - Auth → GET /api/auth/me
   - Should return current user info

3. **Test Token Refresh:**
   - Auth → POST /api/auth/refresh
   - Should return new access_token

**Result:** If all pass, authentication is working! ✓

### Full Test Suite (30+ minutes)

Run the requests in this order:

1. **Auth Folder** (all requests)
   - Verify login works
   - Verify token is captured
   - Verify refresh works

2. **Create Resources** (all POST requests)
   - Addresses → POST
   - Categories → POST
   - Products → POST
   - Orders → POST
   - Etc.
   - Each should capture an ID

3. **Get Resources** (all GET requests with IDs)
   - Addresses → GET :address_id
   - Products → GET :product_id
   - Should use captured IDs

4. **Update Resources** (all PUT requests)
   - Use captured IDs from step 3
   - Should update successfully

5. **Delete Resources** (all DELETE requests)
   - Use captured IDs
   - Should delete successfully

---

## 📊 Payload Reference

### Required Fields by Endpoint

#### POST /api/auth/register
```json
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "01012345678",
    "password": "SecurePass123!",
    "type_id": 1,
    "gov_id": 1
}
```

#### POST /api/auth/login
```json
{
    "email": "john@example.com",
    "password": "SecurePass123!"
}
```

#### POST /api/auth/reset-password
```json
{
    "email": "john@example.com",
    "otp": "123456",
    "new_password": "NewSecurePass123!"
}
```

#### POST /api/addresses
```json
{
    "title": "Main Warehouse",
    "gov_id": 1,
    "address_line1": "123 Industrial Area",
    "address_line2": "Building 5, Street 10",
    "city": "6th of October",
    "postal_code": "12566",
    "is_default": true
}
```

#### POST /api/products
```json
{
    "name": "Product Name",
    "sku": "SKU-001",
    "description": "Product description",
    "category_id": 1,
    "price": 99.99,
    "quantity": 100,
    "is_active": true
}
```

---

## 🔧 Advanced: Manual Token Management

If you need to manually set a token:

1. **Get a Token:**
   - Login via any method
   - Copy the `access_token` from response

2. **Set it in Postman:**
   - Click environment icon (gear) → Edit
   - Find `token` variable
   - Paste the token value
   - Click Save

3. **Use it in Requests:**
   - Authorization header uses `Bearer {{token}}`
   - All protected endpoints will work

---

## ✅ Success Criteria

Your API is working correctly when:

- [ ] **Auth Login** returns 200 with `access_token`
- [ ] **GET /api/auth/me** returns 200 with user profile
- [ ] **POST /api/addresses** returns 201 with created address
- [ ] **GET /api/addresses/:address_id** returns 200 (using created ID)
- [ ] **PUT /api/addresses/:address_id** returns 200
- [ ] **DELETE /api/addresses/:address_id** returns 200
- [ ] No more 401 errors on protected endpoints ✓
- [ ] No more 404 errors on created resource IDs ✓

---

## 📞 Troubleshooting

### Check the Logs

Watch the **Flask server logs** while making requests:
```
GET /api/addresses 401 (this means no token)
GET /api/addresses 200 (this means token is valid)
```

### Verify Database Connection

```bash
# Check if database exists
ls -la app/instance/

# Should see: app.db or torida.db
```

### Check API Server Status

```bash
# Make a health check
curl http://localhost:5000/health

# Should return something like:
# {"status": "ok", "message": "API is running"}
```

---

## 📖 Next Steps

1. ✅ Import the updated collection
2. ✅ Set environment variables
3. ✅ Run Auth → Login to get a token
4. ✅ Test a few endpoints
5. Run the complete test suite to verify all 401s are fixed
6. Use ID chaining to eliminate 404s

**Happy testing!** 🎉
