#!/usr/bin/env python3
"""
TORIDA API - Comprehensive Local Test Suite
============================================
Tests ALL endpoints against the local Flask backend (http://localhost:5000).

Usage:
    $env:PYTHONIOENCODING='utf-8'; python test_all_apis.py
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import time
import sys

BASE_URL = "http://127.0.0.1:5000"

# --- Colours (ANSI) ---
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# --- State ---
results = []
access_token = None
refresh_token = None
user_id = None
supplier_token = None
supplier_id = None
test_product_id = None
test_order_id = None
test_review_id = None
test_address_id = None
test_category_id = None
test_payment_id = None

# Test user credentials (unique per run)
ts = int(time.time())
TEST_USER = {
    "full_name": "API Test Retailer",
    "phone": f"010{str(ts)[-8:]}",
    "email": f"retailer_{ts}@test.com",
    "password": "TestPass123!",
    "type_id": 2,   # Retailer
    "gov_id": 1      # Cairo
}

TEST_SUPPLIER = {
    "full_name": "API Test Supplier",
    "phone": f"011{str(ts)[-8:]}",
    "email": f"supplier_{ts}@test.com",
    "password": "TestPass123!",
    "type_id": 1,   # Supplier
    "gov_id": 1      # Cairo
}


def log(icon, msg, color=RESET):
    print(f"  {color}{icon}{RESET} {msg}")


def make_request(method, url, data=None, token=None):
    """Make HTTP request, return (status, body_dict, ms)."""
    full_url = f"{BASE_URL}{url}"
    body_bytes = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(full_url, data=body_bytes, headers=headers, method=method)
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            elapsed = int((time.perf_counter() - start) * 1000)
            raw = resp.read().decode("utf-8")
            try:
                body_json = json.loads(raw)
            except Exception:
                body_json = {"raw": raw[:500]}
            return resp.getcode(), body_json, elapsed
    except urllib.error.HTTPError as e:
        elapsed = int((time.perf_counter() - start) * 1000)
        raw = e.read().decode("utf-8")
        try:
            body_json = json.loads(raw)
        except Exception:
            body_json = {"raw": raw[:500]}
        return e.code, body_json, elapsed
    except Exception as ex:
        elapsed = int((time.perf_counter() - start) * 1000)
        return 0, {"error": str(ex)}, elapsed


def test(name, method, url, data=None, token=None, expected=200):
    """Run a single test and record the result."""
    status, body, ms = make_request(method, url, data, token)

    if isinstance(expected, (list, tuple)):
        passed = status in expected
    else:
        passed = status == expected

    icon = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    status_color = GREEN if passed else RED
    result_str = "PASS" if passed else "FAIL"
    detail = body.get("message", "") if isinstance(body, dict) else ""

    print(f"  [{icon}] {BOLD}{method:6s} {url}{RESET}  -> {status_color}{status}{RESET}  ({ms}ms)  {detail}")

    if not passed:
        snippet = json.dumps(body, indent=2)[:300]
        for line in snippet.split("\n"):
            print(f"         {RED}{line}{RESET}")

    results.append((name, method, url, status, result_str, ms, detail))
    return status, body, passed


# ============================
#  1. ROOT & HEALTH CHECK
# ============================
def test_root_health():
    print(f"\n{CYAN}{BOLD}=== 1. Root & Health Check ==={RESET}")
    test("Root", "GET", "/")
    test("Health", "GET", "/health")
    test("API Info", "GET", "/api")
    test("404 Handler", "GET", "/nonexistent-route", expected=404)


# ============================
#  2. PUBLIC ENDPOINTS
# ============================
def test_public():
    print(f"\n{CYAN}{BOLD}=== 2. Public Endpoints ==={RESET}")
    test("List Governorates", "GET", "/api/governorates")
    test("Get Governorate #1", "GET", "/api/governorates/1")
    test("Get Governorate #999", "GET", "/api/governorates/999", expected=404)
    test("List User Types", "GET", "/api/user-types")
    test("Get User Type #1", "GET", "/api/user-types/1")
    test("List Categories", "GET", "/api/categories")
    test("List Products", "GET", "/api/products?page=1&per_page=10")
    test("Products Search", "GET", "/api/products?search=test")


# ============================
#  3. AUTHENTICATION
# ============================
def test_auth():
    global access_token, refresh_token, user_id
    global supplier_token, supplier_id
    print(f"\n{CYAN}{BOLD}=== 3. Authentication ==={RESET}")

    # --- Register Retailer ---
    s, b, ok = test("Register Retailer", "POST", "/api/auth/register",
                     data=TEST_USER, expected=201)
    if ok and isinstance(b, dict):
        d = b.get("data", {})
        if isinstance(d, dict):
            access_token = d.get("access_token")
            refresh_token = d.get("refresh_token")
            u = d.get("user", {})
            if isinstance(u, dict):
                user_id = u.get("id")

    # --- Register Supplier ---
    s2, b2, ok2 = test("Register Supplier", "POST", "/api/auth/register",
                        data=TEST_SUPPLIER, expected=201)
    if ok2 and isinstance(b2, dict):
        d2 = b2.get("data", {})
        if isinstance(d2, dict):
            supplier_token = d2.get("access_token")
            u2 = d2.get("user", {})
            if isinstance(u2, dict):
                supplier_id = u2.get("id")

    # --- Login ---
    s3, b3, ok3 = test("Login Retailer", "POST", "/api/auth/login",
                        data={"email": TEST_USER["email"], "password": TEST_USER["password"]})
    if ok3 and isinstance(b3, dict):
        d3 = b3.get("data", {})
        if isinstance(d3, dict):
            access_token = d3.get("access_token", access_token)
            refresh_token = d3.get("refresh_token", refresh_token)

    # --- Bad Login ---
    test("Login Bad Password", "POST", "/api/auth/login",
         data={"email": TEST_USER["email"], "password": "wrong"}, expected=401)

    test("Login Missing Fields", "POST", "/api/auth/login",
         data={"email": TEST_USER["email"]}, expected=400)

    # --- Get /me ---
    test("Get /me", "GET", "/api/auth/me", token=access_token)

    # --- /me without token ---
    test("Get /me (no token)", "GET", "/api/auth/me", expected=401)

    # --- Refresh ---
    if refresh_token:
        s4, b4, ok4 = test("Refresh Token", "POST", "/api/auth/refresh",
                            data={"refresh_token": refresh_token})
        if ok4 and isinstance(b4, dict):
            d4 = b4.get("data", {})
            if isinstance(d4, dict):
                access_token = d4.get("access_token", access_token)
                refresh_token = d4.get("refresh_token", refresh_token)

    # --- Change Password ---
    test("Change Password", "POST", "/api/auth/change-password",
         data={"current_password": TEST_USER["password"], "new_password": "NewPass123!"},
         token=access_token)
    test("Revert Password", "POST", "/api/auth/change-password",
         data={"current_password": "NewPass123!", "new_password": TEST_USER["password"]},
         token=access_token)

    # --- Forgot Password ---
    test("Forgot Password", "POST", "/api/auth/forgot-password",
         data={"email": TEST_USER["email"]})


# ============================
#  4. USER MANAGEMENT
# ============================
def test_users():
    print(f"\n{CYAN}{BOLD}=== 4. User Management ==={RESET}")
    test("List Users", "GET", "/api/users", token=access_token)
    test("List Users (no token)", "GET", "/api/users", expected=401)

    if user_id:
        test(f"Get User #{user_id}", "GET", f"/api/users/{user_id}", token=access_token)
        test(f"Update User #{user_id}", "PUT", f"/api/users/{user_id}",
             data={"full_name": "Updated Test Retailer"}, token=access_token)
        test(f"Get User Roles #{user_id}", "GET", f"/api/users/{user_id}/roles",
             token=access_token)


# ============================
#  5. CATEGORIES CRUD
# ============================
def test_categories():
    global test_category_id
    print(f"\n{CYAN}{BOLD}=== 5. Categories CRUD ==={RESET}")

    s, b, ok = test("Create Category", "POST", "/api/categories",
                     data={"category_name": f"TestCat_{ts}", "description": "API test category"},
                     token=access_token, expected=(200, 201))
    if ok and isinstance(b, dict):
        d = b.get("data", {})
        if isinstance(d, dict):
            test_category_id = d.get("id")

    if test_category_id:
        test(f"Get Category #{test_category_id}", "GET", f"/api/categories/{test_category_id}")
        test(f"Update Category #{test_category_id}", "PUT", f"/api/categories/{test_category_id}",
             data={"category_name": f"UpdatedCat_{ts}"}, token=access_token)


# ============================
#  6. PRODUCTS CRUD
# ============================
def test_products():
    global test_product_id
    print(f"\n{CYAN}{BOLD}=== 6. Products CRUD ==={RESET}")

    tok = supplier_token or access_token
    cat_id = test_category_id or 1

    s, b, ok = test("Create Product", "POST", "/api/products",
                     data={
                         "product_name": f"TestProduct_{ts}",
                         "description": "API test product",
                         "category_id": cat_id,
                         "price": 99.99,
                         "stock_quantity": 100,
                         "unit": "piece"
                     }, token=tok, expected=(200, 201))
    if ok and isinstance(b, dict):
        d = b.get("data", {})
        if isinstance(d, dict):
            test_product_id = d.get("id")

    test("Products Page 1", "GET", "/api/products?page=1&per_page=5")

    if test_product_id:
        test(f"Get Product #{test_product_id}", "GET", f"/api/products/{test_product_id}")
        test(f"Update Product #{test_product_id}", "PUT", f"/api/products/{test_product_id}",
             data={"product_name": f"Updated_{ts}", "price": 149.99}, token=tok)


# ============================
#  7. CART
# ============================
def test_cart():
    print(f"\n{CYAN}{BOLD}=== 7. Cart ==={RESET}")
    test("Get Cart", "GET", "/api/cart", token=access_token)

    if test_product_id:
        test("Add to Cart", "POST", "/api/cart/items",
             data={"product_id": test_product_id, "quantity": 2},
             token=access_token, expected=(200, 201))

    s, b, ok = test("Get Cart (after add)", "GET", "/api/cart", token=access_token)

    cart_item_id = None
    if ok and isinstance(b, dict):
        d = b.get("data", {})
        items = []
        if isinstance(d, dict):
            items = d.get("items", [])
        elif isinstance(d, list):
            items = d
        if items and isinstance(items[0], dict):
            cart_item_id = items[0].get("id")

    if cart_item_id:
        test(f"Update Cart Item #{cart_item_id}", "PUT", f"/api/cart/items/{cart_item_id}",
             data={"quantity": 5}, token=access_token)
        test(f"Delete Cart Item #{cart_item_id}", "DELETE", f"/api/cart/items/{cart_item_id}",
             token=access_token)

    # Clear cart = DELETE /api/cart (not /api/cart/clear)
    test("Clear Cart", "DELETE", "/api/cart", token=access_token)


# ============================
#  8. WISHLIST
# ============================
def test_wishlist():
    print(f"\n{CYAN}{BOLD}=== 8. Wishlist ==={RESET}")
    test("Get Wishlist", "GET", "/api/wishlist", token=access_token)

    if test_product_id:
        test("Add to Wishlist", "POST", "/api/wishlist",
             data={"product_id": test_product_id},
             token=access_token, expected=(200, 201))
        test("Get Wishlist (after add)", "GET", "/api/wishlist", token=access_token)
        test(f"Remove from Wishlist", "DELETE", f"/api/wishlist/{test_product_id}",
             token=access_token)


# ============================
#  9. ADDRESSES
# ============================
def test_addresses():
    global test_address_id
    print(f"\n{CYAN}{BOLD}=== 9. Addresses ==={RESET}")
    test("List Addresses", "GET", "/api/addresses", token=access_token)

    s, b, ok = test("Create Address", "POST", "/api/addresses",
                     data={
                         "gov_id": 1,
                         "city": "Nasr City",
                         "street": "123 Test Street",
                         "full_address": "Nasr City, 123 Test Street",
                         "label": "Home",
                         "postal_code": "11765",
                         "is_default": True
                     }, token=access_token, expected=(200, 201))
    if ok and isinstance(b, dict):
        d = b.get("data", {})
        if isinstance(d, dict):
            test_address_id = d.get("id")

    if test_address_id:
        test(f"Get Address #{test_address_id}", "GET", f"/api/addresses/{test_address_id}",
             token=access_token)
        test(f"Update Address #{test_address_id}", "PUT", f"/api/addresses/{test_address_id}",
             data={"city": "Maadi", "street": "456 Updated St"},
             token=access_token)


# ============================
# 10. ORDERS
# ============================
def test_orders():
    global test_order_id
    print(f"\n{CYAN}{BOLD}=== 10. Orders ==={RESET}")
    test("List Orders", "GET", "/api/orders", token=access_token)

    if test_product_id:
        # Re-add item to cart for order
        test("Cart: Add item for order", "POST", "/api/cart/items",
             data={"product_id": test_product_id, "quantity": 2},
             token=access_token, expected=(200, 201))

        s, b, ok = test("Create Order", "POST", "/api/orders",
                         data={
                             "items": [{"product_id": test_product_id, "quantity": 2, "unit": "piece"}],
                             "delivery_address_id": test_address_id or 1,
                             "notes": "API test order"
                         }, token=access_token, expected=(200, 201))
        if ok and isinstance(b, dict):
            d = b.get("data", {})
            if isinstance(d, dict):
                test_order_id = d.get("id")

    if test_order_id:
        test(f"Get Order #{test_order_id}", "GET", f"/api/orders/{test_order_id}",
             token=access_token)
        test(f"Order History #{test_order_id}", "GET",
             f"/api/orders/{test_order_id}/history", token=access_token)


# ============================
# 11. PAYMENTS
# ============================
def test_payments():
    global test_payment_id
    print(f"\n{CYAN}{BOLD}=== 11. Payments ==={RESET}")

    if test_order_id:
        # Create payment (field is 'method', not 'payment_method')
        s, b, ok = test("Create Payment", "POST", "/api/payments",
                         data={
                             "order_id": test_order_id,
                             "method": "cash_on_delivery"
                         }, token=access_token, expected=(200, 201))
        if ok and isinstance(b, dict):
            d = b.get("data", {})
            if isinstance(d, dict):
                test_payment_id = d.get("id")

        # Get payment by order
        test(f"Get Payment for Order #{test_order_id}", "GET",
             f"/api/payments/order/{test_order_id}", token=access_token)

        if test_payment_id:
            # Process payment
            test(f"Process Payment #{test_payment_id}", "POST",
                 f"/api/payments/{test_payment_id}/pay", token=access_token)


# ============================
# 12. REVIEWS
# ============================
def test_reviews():
    global test_review_id
    print(f"\n{CYAN}{BOLD}=== 12. Reviews ==={RESET}")

    if test_product_id:
        # GET reviews by product (actual route is /api/reviews/product/<id>)
        test(f"Reviews for Product #{test_product_id}", "GET",
             f"/api/reviews/product/{test_product_id}")

        s, b, ok = test("Create Review", "POST", "/api/reviews",
                         data={
                             "product_id": test_product_id,
                             "rating": 5,
                             "comment": "Excellent test product!"
                         }, token=access_token, expected=(200, 201))
        if ok and isinstance(b, dict):
            d = b.get("data", {})
            if isinstance(d, dict):
                test_review_id = d.get("id")

        if test_review_id:
            test(f"Update Review #{test_review_id}", "PUT",
                 f"/api/reviews/{test_review_id}",
                 data={"rating": 4, "comment": "Updated review"},
                 token=access_token)

    # My reviews
    test("My Reviews", "GET", "/api/reviews/my-reviews", token=access_token)


# ============================
# 13. NOTIFICATIONS
# ============================
def test_notifications():
    print(f"\n{CYAN}{BOLD}=== 13. Notifications ==={RESET}")
    s, b, ok = test("List Notifications", "GET", "/api/notifications", token=access_token)

    # Unread count
    test("Unread Count", "GET", "/api/notifications/unread-count", token=access_token)

    notif_id = None
    if ok and isinstance(b, dict):
        d = b.get("data", [])
        if isinstance(d, list) and d:
            notif_id = d[0].get("id") if isinstance(d[0], dict) else None

    if notif_id:
        test(f"Get Notification #{notif_id}", "GET",
             f"/api/notifications/{notif_id}", token=access_token)
        # Mark single as read: POST /api/notifications/<id>/read
        test(f"Mark Read #{notif_id}", "POST",
             f"/api/notifications/{notif_id}/read", token=access_token)

    # Mark all read: POST /api/notifications/read-all
    test("Mark All Read", "POST", "/api/notifications/read-all", token=access_token)


# ============================
# 14. ROLES & PERMISSIONS
# ============================
def test_roles_permissions():
    print(f"\n{CYAN}{BOLD}=== 14. Roles & Permissions ==={RESET}")
    test("List Roles", "GET", "/api/roles", token=access_token)
    test("List Permissions", "GET", "/api/permissions", token=access_token)
    test("Get Role #1", "GET", "/api/roles/1", token=access_token, expected=(200, 404))
    test("Role #1 Permissions", "GET", "/api/roles/1/permissions", token=access_token, expected=(200, 404))


# ============================
# 15. BUSINESS PROFILES
# ============================
def test_business_profiles():
    print(f"\n{CYAN}{BOLD}=== 15. Business Profiles ==={RESET}")
    # All routes require auth
    test("List Business Profiles", "GET", "/api/business-profiles", token=access_token)

    # Create requires business_name + address
    tok = supplier_token or access_token
    s, b, ok = test("Create Business Profile", "POST", "/api/business-profiles",
                     data={
                         "business_name": f"TestBiz_{ts}",
                         "address": "123 Business St, Cairo"
                     }, token=tok, expected=(200, 201, 400))

    bp_user_id = supplier_id or user_id
    if bp_user_id:
        test(f"Get Business Profile #{bp_user_id}", "GET",
             f"/api/business-profiles/{bp_user_id}", token=tok, expected=(200, 404))


# ============================
# 16. CANCEL ORDER (before cleanup)
# ============================
def test_cancel_order():
    print(f"\n{CYAN}{BOLD}=== 16. Cancel Order ==={RESET}")
    if test_order_id:
        test(f"Cancel Order #{test_order_id}", "POST",
             f"/api/orders/{test_order_id}/cancel", token=access_token, expected=(200, 400))


# ============================
# 17. CLEANUP
# ============================
def test_cleanup():
    print(f"\n{CYAN}{BOLD}=== 17. Cleanup ==={RESET}")

    if test_review_id:
        test(f"Delete Review #{test_review_id}", "DELETE",
             f"/api/reviews/{test_review_id}", token=access_token)
    if test_address_id:
        test(f"Delete Address #{test_address_id}", "DELETE",
             f"/api/addresses/{test_address_id}", token=access_token)
    if test_product_id:
        tok = supplier_token or access_token
        test(f"Delete Product #{test_product_id}", "DELETE",
             f"/api/products/{test_product_id}", token=tok)
    if test_category_id:
        test(f"Delete Category #{test_category_id}", "DELETE",
             f"/api/categories/{test_category_id}", token=access_token)
    if user_id:
        test(f"Delete User #{user_id}", "DELETE",
             f"/api/users/{user_id}", token=access_token, expected=(200, 403))
    if supplier_id:
        test(f"Delete Supplier #{supplier_id}", "DELETE",
             f"/api/users/{supplier_id}", token=supplier_token, expected=(200, 403))

    test("Logout", "POST", "/api/auth/logout", token=access_token)


# ============================
# SUMMARY
# ============================
def print_summary():
    total = len(results)
    passed = sum(1 for r in results if r[4] == "PASS")
    failed = sum(1 for r in results if r[4] == "FAIL")
    rate = (passed / total * 100) if total else 0

    print(f"\n{'=' * 60}")
    print(f"{BOLD}  TORIDA API Test Summary{RESET}")
    print(f"{'=' * 60}")
    print(f"  Total:   {total}")
    print(f"  {GREEN}Passed:  {passed}{RESET}")
    print(f"  {RED}Failed:  {failed}{RESET}")
    print(f"  Rate:    {rate:.1f}%")
    print(f"{'=' * 60}")

    if failed:
        print(f"\n{RED}{BOLD}  Failed Tests:{RESET}")
        for r in results:
            if r[4] == "FAIL":
                print(f"    {RED}x{RESET} {r[1]:6s} {r[2]}  -> {r[3]}  {r[6]}")
        print()

    return failed == 0


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print(f"\n{BOLD}{'=' * 60}")
    print(f"  TORIDA API - Comprehensive Local Test Suite")
    print(f"  Target: {BASE_URL}")
    print(f"  Time:   {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}{RESET}\n")

    try:
        test_root_health()
        test_public()
        test_auth()
        test_users()
        test_categories()
        test_products()
        test_cart()
        test_wishlist()
        test_addresses()
        test_orders()
        test_payments()
        test_reviews()
        test_notifications()
        test_roles_permissions()
        test_business_profiles()
        test_cancel_order()
        test_cleanup()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted.{RESET}")
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        import traceback
        traceback.print_exc()

    all_passed = print_summary()
    sys.exit(0 if all_passed else 1)
