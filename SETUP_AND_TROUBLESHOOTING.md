# TORIDA Postman Collection - Complete Fix & Setup Guide

## 📋 Summary of Changes

Your Postman collection has been completely overhauled to fix **all 76 authentication failures** and provide framework for fixing **14 resource ID errors**. 

### What Was Fixed

| Issue | Type | Count | Solution |
|-------|------|-------|----------|
| Missing auth token | 401 Unauthorized | 76 | ✅ Auto-login script + token capture |
| Non-existent resource IDs | 404 Not Found | 14 | ✅ ID chaining framework |
| Invalid payloads | 400/422 Validation | 2 | ✅ Payload documentation |

---

## 🎯 Quick Setup (5 minutes)

### Step 1: Ensure Database is Initialized

```bash
# Navigate to project directory
cd c:\Users\COMPUMARTS\Downloads\torida_backend_complete

# Create database tables (if not already done)
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✓ Database tables created')
"
```

### Step 2: Seed Test Data

```bash
# Run the seed script to populate test data
python seed_database.py
```

**Expected Output:**
```
✓ User types seeded
✓ Governorates seeded
✓ Test users seeded
✓ Roles seeded
✓ Permissions seeded
✓ Categories seeded
✓ Products seeded
✓ Addresses seeded
✓ Carts seeded
✓ Wishlists seeded
✓ Orders seeded
✓ Reviews seeded

✓ Test Account:
  Email: john.doe@example.com
  Password: Password123!
```

### Step 3: Start Flask Server

```bash
# In your terminal, activate virtual environment and start server
python app/run.py
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════╗
║                    TORIDA API Server                      ║
║                   B2B Marketplace Backend                 ║
╠═══════════════════════════════════════════════════════════╣
║  Server: http://localhost:5000
║  Health: http://localhost:5000/health
╚═══════════════════════════════════════════════════════════╝
```

### Step 4: Import Collection in Postman

1. Open Postman
2. Click **File** → **Import** (or Ctrl+O)
3. Select **torida_postman_collection.json**
4. Click **Import**

### Step 5: Verify Setup

1. Click the **environment icon** (gear) in top-right
2. Select **Edit** next to active environment
3. Verify these variables exist:
   - `base_url` = `http://localhost:5000`
   - `test_email` = `john.doe@example.com`
   - `test_password` = `Password123!`

4. Click **Save**

### Step 6: Test Login (First Request to Run!)

1. In Postman, go to **Auth** folder
2. Click **POST /api/auth/login**
3. Review the body (should match your test account)
4. Click **Send** (blue button)
5. Should see **200 OK** response with:
   - `access_token`
   - `refresh_token`
   - `user` object with `id`

**Success indicator:** Check the environment variables again - `{{token}}` should now have a value!

---

## 🔍 Understanding the Fixes

### Fix #1: Collection-Level Pre-Request Script

**Location:** Collection Settings → Pre-request Scripts

**What it does:**
```javascript
// Checks if {{token}} is empty
if (!pm.variables.get("token") || pm.variables.get("token") === "") {
    // Auto-login with test credentials
    // Saves token to {{token}}
}
```

**When it runs:** Before EVERY request in the collection

**Result:** Even if you forget to login, the first request will auto-login! ✓

### Fix #2: Login Endpoint Tests Script

**Location:** Auth → POST /api/auth/login → Tests tab

**What it does:**
```javascript
// After successful login:
pm.variables.set("token", data.data.access_token);
pm.variables.set("refresh_token", data.data.refresh_token);
pm.variables.set("user_id", data.data.user.id);
```

**Result:** Token automatically captured and available for all requests ✓

### Fix #3: Resource Creation ID Capture

**Location:** POST endpoints (Products, Orders, etc.) → Tests tab

**What it does:**
```javascript
// After creating a resource:
pm.variables.set("product_id", data.data.id);  // For products
pm.variables.set("order_id", data.data.id);    // For orders
```

**How to use:**
```
1. POST /api/products → captures {{product_id}}
2. GET /api/products/{{product_id}} → uses the captured ID
3. PUT /api/products/{{product_id}} → updates using ID
4. DELETE /api/products/{{product_id}} → deletes using ID
```

---

## 🚀 Testing Workflows

### Workflow 1: Minimal Test (Verify Auth Works)

**Goal:** Confirm the 401 errors are fixed

**Steps:**
1. Go to **Auth** folder
2. Run **POST /api/auth/login**
3. Verify response: 200 OK with `access_token`
4. Run **GET /api/auth/me**
5. Verify response: 200 OK with user profile

**Expected Result:** ✅ 0 more 401 errors on auth endpoints

### Workflow 2: Create & Retrieve Flow (Verify ID Chaining)

**Goal:** Confirm resource ID chaining works

**Steps:**
1. Go to **Products** folder
2. Run **POST /api/products** (create a product)
   - Response should have status 201 or 200
   - Response should include `id` field
   - `{{product_id}}` variable should now be set

3. Run **GET /api/products/{{product_id}}** (get the created product)
   - Response should have status 200
   - Should return the product you just created

**Expected Result:** ✅ 0 more 404 errors on created resource IDs

### Workflow 3: Full CRUD Test

**Goal:** Comprehensive test of Create, Read, Update, Delete

**Example: Products**

```
1. POST /api/products
   └─ Creates product → captures {{product_id}}

2. GET /api/products/{{product_id}}
   └─ Retrieves the created product

3. PUT /api/products/{{product_id}}
   └─ Updates the product using captured ID

4. DELETE /api/products/{{product_id}}
   └─ Deletes the product using captured ID

5. GET /api/products/{{product_id}}
   └─ Should return 404 (product was deleted)
```

**Repeat this for:** Addresses, Categories, Orders, Roles, Users, etc.

---

## ⚠️ Troubleshooting

### Problem 1: Still Getting 401 on Protected Endpoints

**Symptoms:**
- Auth endpoints return 200
- Other endpoints return 401
- `{{token}}` variable is empty or looks weird

**Diagnosis:**
```bash
# Check if the token variable is actually being set
# In Postman: Click environment icon → see if {{token}} has a value
```

**Solutions:**

1. **Manual Fix - Re-login:**
   - Go to **Auth → POST /api/auth/login**
   - Click **Send**
   - Wait for response
   - Check environment - `{{token}}` should have a long string value

2. **Check Credentials:**
   - Verify test account exists: `john.doe@example.com`
   - Verify it's in the database (run seed_database.py if not)

3. **Verify Collection Variables:**
   - Click environment icon (gear) → **Edit**
   - Look for these variables:
     - `base_url`: should be `http://localhost:5000`
     - `token`: should be empty or have a token string
     - `test_email`: should be `john.doe@example.com`
     - `test_password`: should be `Password123!`

4. **Check Authorization Header:**
   - Click any protected request
   - Go to **Headers** tab
   - Should see: `Authorization: Bearer {{token}}`
   - If you see something else, fix it

### Problem 2: Getting 404 on GET /api/products/:product_id

**Symptoms:**
- POST /api/products returns 201 (success)
- GET /api/products/:product_id returns 404 (not found)
- Product ID variable looks correct

**Causes & Solutions:**

1. **Product doesn't exist in database:**
   - Run seed_database.py to create test products
   - Or create a new product first (POST) before trying to GET it

2. **Wrong product ID being used:**
   - Check that POST response actually returned an `id` field
   - Verify `{{product_id}}` variable has a numeric value
   - In Postman: Click environment icon → check `product_id` value

3. **Path parameter not set correctly:**
   - Click the GET request
   - Go to **Params** tab
   - Should see `product_id` with a value
   - Or check URL - should be `/api/products/123` (not `/api/products/:product_id`)

### Problem 3: Getting 422 on POST /api/auth/register

**Symptoms:**
- Register request returns 422 Unprocessable Entity
- Response body shows validation errors

**Solutions:**

Check the 422 response body - it will tell you which field failed. Common issues:

1. **Email already exists:**
   - Use a different email (add timestamp: `john.doe.1234@example.com`)

2. **Phone already exists:**
   - Use a different phone (add digits: `01098765432` instead of `01012345678`)

3. **Invalid password:**
   - Password must be min 8 characters
   - Must include: uppercase, lowercase, number, special character
   - Use: `SecurePass123!` or `NewPassword@456`

4. **Invalid type_id or gov_id:**
   - type_id must be 1, 2, or 3
   - gov_id must exist in database (run seed_database.py)
   - Valid gov_id values: 1-14 (Egyptian governorates)

### Problem 4: API Server Won't Start

**Symptoms:**
- Terminal shows error when running `python app/run.py`
- Port 5000 already in use

**Solutions:**

1. **Port already in use:**
   ```bash
   # Kill the existing process on port 5000
   # On Windows:
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # Then try starting again
   python app/run.py
   ```

2. **Missing dependencies:**
   ```bash
   # Install requirements
   pip install -r requirements.txt
   ```

3. **Database file locked:**
   ```bash
   # Delete old database and recreate
   rm app/instance/app.db
   python -c "from app import create_app, db; app = create_app(); db.create_all()"
   ```

### Problem 5: Postman Can't Connect to localhost:5000

**Symptoms:**
- Postman shows "Could not connect to localhost:5000"
- Or times out after waiting

**Solutions:**

1. **Verify server is running:**
   ```bash
   # In another terminal, test the server
   curl http://localhost:5000/health
   # Should return: {"status": "ok"} or similar
   ```

2. **Try different base_url:**
   - If `localhost` doesn't work, try `127.0.0.1`
   - Click environment icon → Edit
   - Change `base_url` to `http://127.0.0.1:5000`

3. **Check firewall:**
   - Windows Firewall might be blocking it
   - Allow Python through Windows Firewall

4. **Try a GET request first:**
   - Start with something simple: **GET /api**
   - This doesn't require token
   - If it works, then token issues are the problem

---

## 📊 Validation Rules

### User Registration Requirements

```json
{
    "full_name": {
        "type": "string",
        "min_length": 2,
        "required": true
    },
    "email": {
        "type": "email",
        "must_be_unique": true,
        "required": true,
        "example": "john@example.com"
    },
    "phone": {
        "type": "string",
        "format": "Egyptian format",
        "must_be_unique": true,
        "required": true,
        "example": "01012345678"
    },
    "password": {
        "type": "string",
        "min_length": 8,
        "must_contain": ["uppercase", "lowercase", "number", "special_char"],
        "required": true,
        "example": "SecurePass123!"
    },
    "type_id": {
        "type": "integer",
        "allowed_values": [1, 2, 3],
        "meaning": {
            "1": "Supplier",
            "2": "Retailer",
            "3": "Company"
        },
        "required": true
    },
    "gov_id": {
        "type": "integer",
        "allowed_values": "1-14 (Egyptian governorates)",
        "required": true
    }
}
```

### Login Requirements

```json
{
    "email": {
        "type": "email",
        "required": true
    },
    "password": {
        "type": "string",
        "required": true,
        "note": "Must match the registered password"
    }
}
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] **Database created** - `app/instance/app.db` exists
- [ ] **Test data seeded** - Ran `python seed_database.py`
- [ ] **Server running** - `python app/run.py` shows "TORIDA API Server"
- [ ] **Collection imported** - Postman shows "TORIDA API" collection
- [ ] **Environment set** - `base_url`, `test_email`, `test_password` configured
- [ ] **Login works** - Auth → POST /api/auth/login returns 200
- [ ] **Token captured** - `{{token}}` variable has a value after login
- [ ] **Protected endpoint works** - Auth → GET /api/auth/me returns 200
- [ ] **Create resource works** - Products → POST /api/products returns 201
- [ ] **ID chaining works** - Products → GET /api/products/{{product_id}} returns 200

**All checked? You're ready to go!** 🎉

---

## 🎓 How It All Works Together

### The Complete Flow

```
1. Start Postman
   ├─ Collection loads
   └─ Variables initialize (base_url, test_email, test_password)

2. Make a request to any protected endpoint
   ├─ Collection pre-request script runs
   ├─ Checks if {{token}} is empty
   └─ If empty, auto-logs in using test credentials
        ├─ POST /api/auth/login
        ├─ Login Tests script runs
        ├─ Captures access_token → {{token}}
        ├─ Captures refresh_token → {{refresh_token}}
        └─ Captures user_id → {{user_id}}

3. Request proceeds with Authorization header
   ├─ Header: Bearer {{token}}
   ├─ Server validates token
   └─ If valid, request succeeds! ✓

4. For resource creation (POST)
   ├─ Request succeeds (201 or 200)
   ├─ Response contains created resource
   ├─ Tests script captures the ID
   └─ ID saved to variable (e.g., {{product_id}})

5. For resource operations (GET, PUT, DELETE with :id)
   ├─ Use the captured ID from step 4
   ├─ Path becomes /api/products/123 (where 123 is {{product_id}})
   └─ Request succeeds! ✓
```

### Why 401s Are Fixed

**Before:**
```
Request header: Authorization: Bearer {{token}}
Variable {{token}} = "" (empty)
Header becomes: Authorization: Bearer 
Server: No token = 401 Unauthorized ✗
```

**After:**
```
Pre-request script runs:
  - Sees {{token}} is empty
  - Auto-logs in
  - Captures token from response
  - Sets {{token}} = "eyJhbGciOiJIUzI1NiIs..." (real token)

Request header: Authorization: Bearer {{token}}
Header becomes: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Server: Valid token = 200 OK ✓
```

### Why 404s Are Fixed

**Before:**
```
GET /api/products/1
Server: Does product ID 1 exist?
Response: No, it doesn't = 404 Not Found ✗
```

**After:**
```
POST /api/products (create new product)
Response: { id: 123, name: "Product", ... }
Tests script: Save 123 to {{product_id}}

GET /api/products/{{product_id}}
Path becomes: GET /api/products/123
Server: Does product ID 123 exist? Yes!
Response: 200 OK + product details ✓
```

---

## 📞 Still Having Issues?

1. **Check the Server Logs:**
   - Watch the terminal where Flask is running
   - Look for error messages
   - Try making the request again and see what error appears

2. **Check the Response Body:**
   - In Postman, after getting an error
   - Click **Body** tab to see the error message
   - The error message usually tells you exactly what's wrong

3. **Verify Database:**
   ```bash
   # Check if database exists and has tables
   python -c "
   from app import create_app, db
   import sqlalchemy as sa
   app = create_app()
   with app.app_context():
       tables = db.inspect(db.engine).get_table_names()
       print(f'Tables in database: {tables}')
   "
   ```

4. **Verify User Exists:**
   ```bash
   python -c "
   from app import create_app
   from app.models import User
   app = create_app()
   with app.app_context():
       user = User.query.filter_by(email='john.doe@example.com').first()
       if user:
           print(f'✓ User exists: {user.full_name}')
       else:
           print('✗ User not found - run seed_database.py')
   "
   ```

---

## 🎉 You're All Set!

Your Postman collection is now:
- ✅ Fully automated authentication
- ✅ Automatic ID chaining
- ✅ Ready for comprehensive API testing

**Now go test your API and celebrate those fixed errors!** 🚀
