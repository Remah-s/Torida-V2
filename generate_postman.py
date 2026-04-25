import json
import os
import sys
import re

# Add the parent directory to the path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def get_fake_data(path, method):
    """Return realistic fake data based on endpoint path and method."""
    if method not in ['POST', 'PUT', 'PATCH']:
        return None
        
    path = str(path).lower()
    
    # Auth
    if 'auth/register' in path:
        return {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "01012345678",
            "password": "Password123!",
            "type_id": 1,
            "gov_id": 1
        }
    elif 'auth/login' in path:
        return {
            "email": "john.doe@example.com",
            "password": "Password123!"
        }
    elif 'auth/forgot-password' in path:
        return {
            "email": "john.doe@example.com"
        }
    elif 'auth/reset-password' in path:
        return {
            "email": "john.doe@example.com",
            "otp": "123456",
            "new_password": "NewPassword123!"
        }
    elif 'auth/change-password' in path:
        return {
            "current_password": "Password123!",
            "new_password": "NewPassword123!"
        }
    elif 'auth/refresh' in path:
        return {
            "refresh_token": "your_refresh_token_here"
        }
    elif 'auth/verify-email' in path:
        return {
            "otp": "123456"
        }
        
    # Products
    elif 'products' in path and method == 'POST':
        return {
            "name_en": "Premium Office Chair",
            "name_ar": "كرسي مكتب ممتاز",
            "description_en": "Ergonomic mesh office chair with lumbar support",
            "description_ar": "كرسي مكتب مريح مع دعم لأسفل الظهر",
            "category_id": 1,
            "price": 2500.00,
            "stock_quantity": 50,
            "min_order_quantity": 5,
            "status": "active"
        }
    elif 'products' in path and method == 'PUT':
        return {
            "price": 2400.00,
            "stock_quantity": 40
        }
        
    # Categories
    elif 'categories' in path and method == 'POST':
        return {
            "name_en": "Office Furniture",
            "name_ar": "أثاث مكتبي",
            "description_en": "Desks, chairs, and filing cabinets",
            "description_ar": "مكاتب وكراسي وخزائن ملفات",
            "parent_id": None
        }
        
    # Cart
    elif 'cart/items' in path:
        return {
            "product_id": 1,
            "quantity": 10
        }
        
    # Wishlist
    elif 'wishlist' in path:
        return {
            "product_id": 1
        }
        
    # Addresses
    elif 'addresses' in path:
        return {
            "title": "Main Warehouse",
            "gov_id": 1,
            "address_line1": "123 Industrial Area",
            "address_line2": "Building 5, Street 10",
            "city": "6th of October",
            "postal_code": "12566",
            "is_default": True
        }
        
    # Business Profiles
    elif 'business-profiles' in path:
        return {
            "company_name": "Tech Corp Egypt",
            "commercial_register": "CR123456789",
            "tax_id": "TAX987654321",
            "business_type": "Wholesale Distributor",
            "address": "10 Cairo Business Park",
            "website": "https://techcorp.com.eg"
        }
        
    # Orders
    elif 'orders' in path and method == 'POST':
        return {
            "shipping_address_id": 1,
            "billing_address_id": 1,
            "notes": "Deliver during business hours only"
        }
    elif 'orders' in path and 'status' in path:
        return {
            "status": "processing",
            "tracking_number": "TRK88829103"
        }
        
    # Payments
    elif 'payments' in path:
        return {
            "order_id": 1,
            "payment_method": "credit_card",
            "amount": 25000.00,
            "transaction_id": "TXN_991827461"
        }
        
    # Reviews
    elif 'reviews' in path:
        return {
            "product_id": 1,
            "rating": 5,
            "comment": "Excellent quality products, fast shipping."
        }
        
    # Users/Roles/Permissions (Admin)
    elif 'users' in path and method in ['POST', 'PUT']:
        return {
            "full_name": "Jane Smith",
            "phone": "01198765432",
            "type_id": 2,
            "gov_id": 2,
            "is_active": True
        }
    elif 'roles' in path:
        return {
            "role_name": "Inventory Manager"
        }
        
    # Default fallback for any other POST/PUT
    return {
        "example_field": "example_value",
        "notes": "Replace with actual expected schema"
    }

def get_fake_path_vars(path):
    """Return sensible fake data for URL path variables."""
    var_map = {
        "id": "1",
        "user_id": "1",
        "product_id": "1",
        "category_id": "1",
        "order_id": "1",
        "address_id": "1",
        "item_id": "1",
        "token": "reset_token_here",
        "filename": "image.jpg"
    }
    
    path_vars = []
    for match in re.finditer(r'<[^:]*:?([^>]+)>', path):
        var_name = match.group(1)
        value = var_map.get(var_name, "1")
        path_vars.append({
            "key": var_name,
            "value": value
        })
    return path_vars

def get_fake_query_params(path, method):
    """Add useful query parameters for GET listings."""
    if method != 'GET':
        return []
        
    # For common list endpoints, add pagination and filtering
    if any(x in path for x in ['/users', '/products', '/orders', '/categories']) and '<' not in path:
        return [
            {"key": "page", "value": "1", "disabled": True, "description": "Page number"},
            {"key": "per_page", "value": "20", "disabled": True, "description": "Items per page"},
            {"key": "search", "value": "keyword", "disabled": True, "description": "Search query"},
            {"key": "sort_by", "value": "created_at", "disabled": True, "description": "Sort field"},
            {"key": "order", "value": "desc", "disabled": True, "description": "Sort order (asc/desc)"}
        ]
    return []

def generate_postman_collection():
    app = create_app()
    
    collection = {
        "info": {
            "name": "TORIDA API (with fake data)",
            "description": "B2B Marketplace Backend for Egypt - Full API Collection with Sample Data",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:5000",
                "type": "string"
            },
            {
                "key": "token",
                "value": "your_access_token_here",
                "type": "string"
            }
        ]
    }
    
    folders = {}
    ignore_endpoints = ['static']
    ignore_methods = ['HEAD', 'OPTIONS']
    
    with app.app_context():
        for rule in app.url_map.iter_rules():
            endpoint = rule.endpoint
            
            if endpoint in ignore_endpoints:
                continue
                
            path = str(rule)
            
            parts = path.strip('/').split('/')
            folder_name = "General"
            if len(parts) > 1 and parts[0] == "api":
                folder_name = parts[1].replace('_', ' ').title()
            elif len(parts) > 0 and parts[0]:
                folder_name = parts[0].replace('_', ' ').title()
                
            if folder_name not in folders:
                folders[folder_name] = []
                
            for method in rule.methods:
                if method in ignore_methods:
                    continue
                    
                postman_path = re.sub(r'<[^:]*:?([^>]+)>', r':\1', path)
                path_vars = get_fake_path_vars(path)
                query_params = get_fake_query_params(path, method)
                url_path = postman_path.strip('/').split('/')
                
                item = {
                    "name": f"{method} {path}",
                    "request": {
                        "method": method,
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{token}}",
                                "type": "text"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json",
                                "type": "text"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}" + postman_path + ("" if not query_params else "?page=1&per_page=20"),
                            "host": ["{{base_url}}"],
                            "path": url_path,
                            "variable": path_vars,
                            "query": query_params
                        }
                    },
                    "response": []
                }
                
                # Make token optional for some auth routes
                if 'auth/login' in path or 'auth/register' in path or 'auth/forgot' in path:
                    item["request"]["header"][0]["disabled"] = True
                
                # Add sample JSON body
                fake_data = get_fake_data(path, method)
                if fake_data:
                    item["request"]["body"] = {
                        "mode": "raw",
                        "raw": json.dumps(fake_data, indent=4),
                        "options": {
                            "raw": {"language": "json"}
                        }
                    }
                    
                folders[folder_name].append(item)
                
    # Build folder structure
    for folder_name in sorted(folders.keys()):
        collection["item"].append({
            "name": folder_name,
            "item": folders[folder_name]
        })
        
    output_file = 'torida_postman_collection.json'
    with open(output_file, 'w') as f:
        json.dump(collection, f, indent=4)
        
    print(f"Postman collection generated successfully: {output_file}")

if __name__ == "__main__":
    generate_postman_collection()
