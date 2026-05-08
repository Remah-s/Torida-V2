#!/usr/bin/env python
"""
Fix Postman Collection - Add Auto-Auth and ID Chaining
========================================================
This script updates the TORIDA Postman collection to:
1. Add collection-level pre-request script for auto-login
2. Add Tests scripts to capture tokens and resource IDs
3. Ensure all protected endpoints have proper setup
"""

import json
import sys
import os

# Path to collection
COLLECTION_PATH = "torida_postman_collection.json"

# Pre-request script for collection (auto-login if token missing)
COLLECTION_PREREQ = """
// Check if we have a valid token, if not, try to login
if (!pm.variables.get("token") || pm.variables.get("token") === "") {
    console.log("Token missing, attempting auto-login...");
    
    // Check if we have credentials
    const email = pm.variables.get("test_email") || "john.doe@example.com";
    const password = pm.variables.get("test_password") || "Password123!";
    
    // Make login request
    pm.sendRequest({
        url: pm.variables.get("base_url") + "/api/auth/login",
        method: "POST",
        header: {
            "Content-Type": "application/json"
        },
        body: {
            mode: "raw",
            raw: JSON.stringify({
                email: email,
                password: password
            })
        }
    }, function (err, response) {
        if (err) {
            console.error("Auto-login failed:", err);
        } else {
            try {
                const data = response.json();
                if (data.data && data.data.access_token) {
                    pm.variables.set("token", data.data.access_token);
                    if (data.data.refresh_token) {
                        pm.variables.set("refresh_token", data.data.refresh_token);
                    }
                    if (data.data.user && data.data.user.id) {
                        pm.variables.set("user_id", data.data.user.id);
                    }
                    console.log("Auto-login successful! Token set.");
                } else {
                    console.warn("Login response missing token data");
                }
            } catch (e) {
                console.error("Failed to parse login response:", e);
            }
        }
    });
}
"""

# Tests script for login endpoint (capture token)
LOGIN_TESTS = """
if (pm.response.code === 200) {
    try {
        const data = pm.response.json();
        
        // Save access token
        if (data.data && data.data.access_token) {
            pm.variables.set("token", data.data.access_token);
            console.log("✓ Access token saved");
        }
        
        // Save refresh token
        if (data.data && data.data.refresh_token) {
            pm.variables.set("refresh_token", data.data.refresh_token);
            console.log("✓ Refresh token saved");
        }
        
        // Save user ID
        if (data.data && data.data.user && data.data.user.id) {
            pm.variables.set("user_id", data.data.user.id);
            console.log("✓ User ID saved: " + data.data.user.id);
        }
        
        pm.test("Login successful", function () {
            pm.expect(pm.response.code).to.equal(200);
            pm.expect(data.data.access_token).to.exist;
        });
    } catch (e) {
        console.error("Error parsing login response:", e);
    }
} else {
    pm.test("Login failed", function () {
        pm.expect(pm.response.code).to.equal(200);
    });
}
"""

# Tests script for register endpoint (capture token and user ID)
REGISTER_TESTS = """
if (pm.response.code === 201 || pm.response.code === 200) {
    try {
        const data = pm.response.json();
        
        // Save tokens
        if (data.data && data.data.access_token) {
            pm.variables.set("token", data.data.access_token);
            console.log("✓ Access token saved");
        }
        
        if (data.data && data.data.refresh_token) {
            pm.variables.set("refresh_token", data.data.refresh_token);
            console.log("✓ Refresh token saved");
        }
        
        pm.test("Registration successful", function () {
            pm.expect(pm.response.code).to.be.oneOf([200, 201]);
            pm.expect(data.data.access_token).to.exist;
        });
    } catch (e) {
        console.error("Error parsing register response:", e);
    }
} else {
    pm.test("Registration failed - check payload", function () {
        pm.expect(pm.response.code).to.be.oneOf([200, 201]);
    });
}
"""

# Generic resource creation Tests (capture ID)
def create_resource_capture_tests(resource_name, id_field="id"):
    """Generate a Tests script that captures the created resource ID"""
    return f"""
if (pm.response.code === 201 || pm.response.code === 200) {{
    try {{
        const data = pm.response.json();
        
        // Capture the resource ID
        let id = null;
        if (data.data && data.data.{id_field}) {{
            id = data.data.{id_field};
        }} else if (data.data && data.data.id) {{
            id = data.data.id;
        }}
        
        if (id) {{
            // Save with generic name and resource-specific name
            pm.variables.set("last_created_id", id);
            pm.variables.set("{resource_name}_id", id);
            console.log("✓ {resource_name} ID captured: " + id);
        }}
    }} catch (e) {{
        console.error("Error capturing resource ID:", e);
    }}
}}
"""

def load_collection():
    """Load the Postman collection"""
    with open(COLLECTION_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_collection(collection):
    """Save the updated Postman collection"""
    with open(COLLECTION_PATH, 'w', encoding='utf-8') as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    print(f"✓ Collection saved to {COLLECTION_PATH}")

def add_collection_variables(collection):
    """Add or update collection-level variables"""
    if "variable" not in collection:
        collection["variable"] = []
    
    # Define required variables
    required_vars = [
        {"key": "base_url", "value": "http://localhost:5000", "type": "string"},
        {"key": "token", "value": "", "type": "string"},
        {"key": "refresh_token", "value": "", "type": "string"},
        {"key": "user_id", "value": "", "type": "string"},
        {"key": "test_email", "value": "john.doe@example.com", "type": "string"},
        {"key": "test_password", "value": "Password123!", "type": "string"},
    ]
    
    # Add missing variables
    existing_keys = {v.get("key") for v in collection["variable"]}
    for var in required_vars:
        if var["key"] not in existing_keys:
            collection["variable"].append(var)
    
    print("✓ Collection variables initialized")

def add_collection_prereq(collection):
    """Add pre-request script to collection"""
    if "event" not in collection:
        collection["event"] = []
    
    # Check if pre-request script already exists
    prereq_exists = any(e.get("listen") == "prerequest" for e in collection.get("event", []))
    
    if not prereq_exists:
        collection["event"].append({
            "listen": "prerequest",
            "script": {
                "type": "text/javascript",
                "exec": COLLECTION_PREREQ.strip().split('\n')
            }
        })
        print("✓ Collection-level pre-request script added")
    else:
        print("ⓘ Collection pre-request script already exists")

def add_script_to_request(request_item, script_type, script_content):
    """Add a script to a request's event handlers"""
    if "event" not in request_item:
        request_item["event"] = []
    
    # Check if script already exists
    existing = any(e.get("listen") == script_type for e in request_item.get("event", []))
    if not existing:
        request_item["event"].append({
            "listen": script_type,
            "script": {
                "type": "text/javascript",
                "exec": script_content.strip().split('\n')
            }
        })
        return True
    return False

def process_requests(items, path=""):
    """Recursively process all requests in the collection"""
    for item in items:
        current_path = f"{path}/{item.get('name', '')}"
        
        if "item" in item:
            # Folder - recurse into it
            process_requests(item["item"], current_path)
        elif "request" in item:
            # Request - add appropriate scripts
            request_obj = item["request"]
            request_name = item.get("name", "")
            method = request_obj.get("method", "GET")
            
            # Parse URL to identify endpoint type
            url_parts = request_obj.get("url", {})
            if isinstance(url_parts, str):
                url_str = url_parts
            else:
                path_list = url_parts.get("path", [])
                url_str = "/".join(path_list)
            
            url_lower = url_str.lower()
            
            # Add appropriate Tests scripts
            if "login" in url_lower and method == "POST":
                if add_script_to_request(item, "test", LOGIN_TESTS):
                    print(f"  ✓ Tests script added to: {request_name}")
            
            elif "register" in url_lower and method == "POST":
                if add_script_to_request(item, "test", REGISTER_TESTS):
                    print(f"  ✓ Tests script added to: {request_name}")
            
            elif method == "POST" and "POST" in request_name:
                # For other POST requests that create resources
                resource_type = "resource"
                if "address" in url_lower:
                    resource_type = "address"
                elif "product" in url_lower and "review" not in url_lower:
                    resource_type = "product"
                elif "category" in url_lower:
                    resource_type = "category"
                elif "role" in url_lower:
                    resource_type = "role"
                elif "user" in url_lower and "type" not in url_lower:
                    resource_type = "user"
                elif "permission" in url_lower:
                    resource_type = "permission"
                
                tests_script = create_resource_capture_tests(resource_type)
                if add_script_to_request(item, "test", tests_script):
                    print(f"  ✓ Resource capture script added to: {request_name}")

def main():
    """Main execution"""
    print("=" * 60)
    print("TORIDA Postman Collection - Auto-Fix")
    print("=" * 60)
    
    if not os.path.exists(COLLECTION_PATH):
        print(f"✗ Error: {COLLECTION_PATH} not found")
        return False
    
    print(f"\n1. Loading collection from {COLLECTION_PATH}...")
    collection = load_collection()
    
    print(f"2. Adding collection variables...")
    add_collection_variables(collection)
    
    print(f"3. Adding collection-level pre-request script...")
    add_collection_prereq(collection)
    
    print(f"4. Adding endpoint-specific event scripts...")
    if "item" in collection:
        process_requests(collection["item"])
    
    print(f"\n5. Saving updated collection...")
    save_collection(collection)
    
    print("\n" + "=" * 60)
    print("✓ Postman collection updated successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Import the updated collection into Postman")
    print("2. Set the 'base_url' variable to your API server URL")
    print("3. Update 'test_email' and 'test_password' if needed")
    print("4. Run the Auth > Login request to get a valid token")
    print("5. Other requests will now use the {{token}} variable")
    print("\nNote: The auto-login script will run if {{token}} is empty")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
