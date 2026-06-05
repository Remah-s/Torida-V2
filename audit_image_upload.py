#!/usr/bin/env python
"""Audit image upload and retrieval flow"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import ProductImage, BusinessProfile

app = create_app()

with app.app_context():
    print("\n=== CLOUDINARY CONFIGURATION ===")
    cloud_name = app.config.get('CLOUDINARY_CLOUD_NAME')
    api_key = app.config.get('CLOUDINARY_API_KEY')
    api_secret = app.config.get('CLOUDINARY_API_SECRET')
    public_url = app.config.get('PUBLIC_API_BASE_URL')
    
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key Set: {'YES' if api_key else 'NO'}")
    print(f"API Secret Set: {'YES' if api_secret else 'NO'}")
    print(f"Public URL: {public_url}")
    
    if not all([cloud_name, api_key, api_secret]):
        print("[ERROR] Missing Cloudinary credentials!")
        sys.exit(1)
    
    print("\n=== PRODUCTS WITH IMAGES ===")
    products = db.session.query(ProductImage).limit(5).all()
    if products:
        for img in products:
            print(f"Product ID: {img.product_id}")
            print(f"  URL: {img.image_url[:80]}")
            print(f"  Is HTTPS: {img.image_url.startswith('https://') if img.image_url else 'N/A'}")
    else:
        print("No product images found")
    
    print("\n=== BUSINESS PROFILES WITH IMAGES ===")
    try:
        profiles = db.session.query(BusinessProfile).limit(3).all()
        if profiles:
            for p in profiles:
                print(f"Business: {p.business_name} (User ID: {p.user_id})")
                try:
                    if hasattr(p, 'logo_url') and p.logo_url:
                        print(f"  Logo: {p.logo_url[:80]}")
                    if hasattr(p, 'cover_image_url') and p.cover_image_url:
                        print(f"  Cover: {p.cover_image_url[:80]}")
                except Exception as e:
                    print(f"  Error reading image URLs: {str(e)}")
        else:
            print("No business profiles found")
    except Exception as e:
        print(f"[ERROR] Cannot query business profiles: {str(e)}")
    
    print("\n=== ENVIRONMENT VARIABLES ===")
    env_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET', 'PUBLIC_API_BASE_URL']
    for var in env_vars:
        val = os.getenv(var, 'NOT SET')
        if var in ['CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']:
            val = 'SET' if os.getenv(var) else 'NOT SET'
        print(f"{var}: {val}")
    
    print("\nAudit complete.")
