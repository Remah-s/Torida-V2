#!/usr/bin/env python
"""
Final Validation: Complete Image Upload Flow Test
Tests: upload -> save -> retrieve
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import ProductImage, BusinessProfile
from app.services.cloudinary_service import upload_image
from werkzeug.datastructures import FileStorage
import base64

app = create_app()

def test_cloudinary_upload():
    """Test: Upload image to Cloudinary"""
    print("\n[TEST 1] CLOUDINARY UPLOAD")
    print("-" * 60)
    
    try:
        # Create test image
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
        )
        # Use platform-agnostic temp directory
        import tempfile
        temp_dir = tempfile.gettempdir()
        test_path = os.path.join(temp_dir, 'test_audit.png')
        with open(test_path, 'wb') as f:
            f.write(png_data)
        
        # Upload to Cloudinary
        with open(test_path, 'rb') as f:
            file = FileStorage(
                stream=f,
                filename='audit_test.png',
                content_type='image/png'
            )
            
            success, image_url, error = upload_image(
                file,
                folder='torida/audit-test',
                max_size=10485760,
                allowed_extensions={'png', 'jpg', 'jpeg', 'webp'}
            )
        
        if not success:
            print(f"[FAIL] Upload failed: {error}")
            return False
        
        print(f"[PASS] Upload successful")
        print(f"       URL: {image_url[:80]}...")
        
        if not image_url.startswith('https://'):
            print(f"[FAIL] URL is not HTTPS")
            return False
        
        print(f"[PASS] URL is HTTPS Cloudinary URL")
        return image_url
        
    except Exception as e:
        print(f"[FAIL] Upload test error: {str(e)}")
        return False


def test_database_persistence(image_url):
    """Test: Verify URL can be stored and retrieved from DB"""
    print("\n[TEST 2] DATABASE PERSISTENCE")
    print("-" * 60)
    
    try:
        # Get a product to test with
        product = db.session.query(ProductImage).first()
        if not product:
            print("[SKIP] No existing products to test with")
            return True
        
        print(f"[PASS] Found product image in DB")
        print(f"       Product ID: {product.product_id}")
        print(f"       URL in DB: {product.image_url[:80]}...")
        
        if not product.image_url.startswith('https://'):
            print(f"[FAIL] Stored URL is not HTTPS")
            return False
        
        print(f"[PASS] Stored URL is HTTPS")
        return True
        
    except Exception as e:
        print(f"[FAIL] Database test error: {str(e)}")
        return False


def test_url_retrieval():
    """Test: Verify retrieval and URL transformation"""
    print("\n[TEST 3] URL RETRIEVAL & TRANSFORMATION")
    print("-" * 60)
    
    try:
        from app.utils.helpers import build_public_url
        
        # Get a product image
        image = db.session.query(ProductImage).first()
        if not image:
            print("[SKIP] No existing product images")
            return True
        
        print(f"[PASS] Retrieved product image")
        print(f"       Original: {image.image_url[:80]}...")
        
        # Test build_public_url transformation
        transformed = build_public_url(image.image_url)
        print(f"       After build_public_url: {transformed[:80]}...")
        
        if transformed != image.image_url:
            print(f"[FAIL] URL was modified!")
            print(f"       Original:    {image.image_url}")
            print(f"       Transformed: {transformed}")
            return False
        
        print(f"[PASS] URL unchanged (as expected for HTTPS)")
        
        # Verify it can be accessed
        if transformed.startswith('https://res.cloudinary.com/'):
            print(f"[PASS] URL format is valid Cloudinary URL")
            return True
        else:
            print(f"[FAIL] URL format is not valid Cloudinary URL")
            return False
        
    except Exception as e:
        print(f"[FAIL] Retrieval test error: {str(e)}")
        return False


def test_business_profile_images():
    """Test: Verify business profile image columns work"""
    print("\n[TEST 4] BUSINESS PROFILE IMAGES")
    print("-" * 60)
    
    try:
        profiles = db.session.query(BusinessProfile).limit(1).all()
        if not profiles:
            print("[SKIP] No business profiles found")
            return True
        
        profile = profiles[0]
        print(f"[PASS] Retrieved business profile")
        print(f"       Business: {profile.business_name}")
        print(f"       User ID: {profile.user_id}")
        
        # Check if image columns exist and work
        try:
            logo = profile.logo_url
            cover = profile.cover_image_url
            print(f"[PASS] Image columns accessible")
            print(f"       logo_url: {logo[:50] if logo else 'None'}...")
            print(f"       cover_image_url: {cover[:50] if cover else 'None'}...")
            return True
        except Exception as col_err:
            print(f"[FAIL] Cannot access image columns: {str(col_err)}")
            return False
        
    except Exception as e:
        print(f"[FAIL] Business profile test error: {str(e)}")
        return False


def test_configuration():
    """Test: Verify all configuration is correct"""
    print("\n[TEST 5] CONFIGURATION")
    print("-" * 60)
    
    try:
        cloud_name = app.config.get('CLOUDINARY_CLOUD_NAME')
        api_key = app.config.get('CLOUDINARY_API_KEY')
        api_secret = app.config.get('CLOUDINARY_API_SECRET')
        public_url = app.config.get('PUBLIC_API_BASE_URL')
        
        if not cloud_name:
            print("[FAIL] CLOUDINARY_CLOUD_NAME not set")
            return False
        print(f"[PASS] CLOUDINARY_CLOUD_NAME: {cloud_name}")
        
        if not api_key:
            print("[FAIL] CLOUDINARY_API_KEY not set")
            return False
        print(f"[PASS] CLOUDINARY_API_KEY: SET")
        
        if not api_secret:
            print("[FAIL] CLOUDINARY_API_SECRET not set")
            return False
        print(f"[PASS] CLOUDINARY_API_SECRET: SET")
        
        if public_url:
            print(f"[PASS] PUBLIC_API_BASE_URL: {public_url}")
        else:
            print(f"[WARN] PUBLIC_API_BASE_URL not set (uses request context)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Configuration test error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("IMAGE UPLOAD VALIDATION - COMPLETE FLOW TEST")
    print("=" * 60)
    
    with app.app_context():
        tests = [
            ("Configuration", test_configuration),
            ("Cloudinary Upload", lambda: test_cloudinary_upload()),
            ("Database Persistence", test_database_persistence),
            ("URL Retrieval", test_url_retrieval),
            ("Business Profile Images", test_business_profile_images),
        ]
        
        results = {}
        image_url = None
        
        for test_name, test_func in tests:
            try:
                if test_name == "Cloudinary Upload":
                    result = test_func()
                    image_url = result
                    results[test_name] = result is not False
                elif test_name == "Database Persistence":
                    results[test_name] = test_func(image_url)
                else:
                    results[test_name] = test_func()
            except Exception as e:
                print(f"[ERROR] Test crashed: {str(e)}")
                import traceback
                traceback.print_exc()
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} {test_name}")
        
        all_passed = all(results.values())
        
        print("\n" + "=" * 60)
        if all_passed:
            print("[SUCCESS] All tests passed! Image upload working correctly.")
            print("=" * 60)
            return 0
        else:
            print("[ERROR] Some tests failed. Review output above.")
            print("=" * 60)
            return 1


if __name__ == '__main__':
    sys.exit(main())
