#!/usr/bin/env python
"""
Database Migration: Add image columns to business_profiles table
This script adds the missing logo_url and cover_image_url columns
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("[1] Checking if columns exist...")
        
        # Check if columns already exist
        result = db.session.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'torida' 
            AND TABLE_NAME = 'business_profiles'
            AND COLUMN_NAME IN ('logo_url', 'cover_image_url')
        """))
        
        existing_columns = [row[0] for row in result]
        
        if 'logo_url' in existing_columns:
            print("    [OK] logo_url column exists")
        else:
            print("    [ADDING] logo_url column...")
            db.session.execute(text("""
                ALTER TABLE business_profiles 
                ADD COLUMN logo_url VARCHAR(500) AFTER address
            """))
            print("    [OK] logo_url column added")
        
        if 'cover_image_url' in existing_columns:
            print("    [OK] cover_image_url column exists")
        else:
            print("    [ADDING] cover_image_url column...")
            db.session.execute(text("""
                ALTER TABLE business_profiles 
                ADD COLUMN cover_image_url VARCHAR(500) AFTER logo_url
            """))
            print("    [OK] cover_image_url column added")
        
        db.session.commit()
        print("\n[2] Verification...")
        
        # Verify columns exist
        result = db.session.execute(text("""
            SELECT COLUMN_NAME, COLUMN_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'torida' 
            AND TABLE_NAME = 'business_profiles'
            AND COLUMN_NAME IN ('logo_url', 'cover_image_url')
        """))
        
        for column_name, column_type in result:
            print(f"    [OK] {column_name}: {column_type}")
        
        print("\n[SUCCESS] Migration completed!")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        db.session.rollback()
        sys.exit(1)
