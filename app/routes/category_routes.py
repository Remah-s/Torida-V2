"""
Category Routes
===============
Routes for category management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Category
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination
from app.utils.auth import token_required

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


@category_bp.route('', methods=['GET'])
def get_categories():
    """Get all categories."""
    include_count = request.args.get('include_count', 'false').lower() == 'true'
    
    categories = Category.query.order_by(Category.category_name).all()
    
    if include_count:
        data = [cat.to_dict_with_product_count() for cat in categories]
    else:
        data = [cat.to_dict() for cat in categories]
    
    return success_response(data)


@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID."""
    category = Category.query.get(category_id)
    
    if not category:
        return not_found_response("Category not found")
    
    return success_response(category.to_dict_with_product_count())


@category_bp.route('', methods=['POST'])
@token_required
def create_category():
    """Create a new category."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['category_name']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Check if category name already exists
    if Category.query.filter_by(category_name=data['category_name']).first():
        return error_response("Category name already exists", 400)
    
    try:
        category = Category(category_name=data['category_name'])
        db.session.add(category)
        db.session.commit()
        
        # Update custom_id
        category.custom_id = f"CAT-{category.id}"
        db.session.commit()
        
        return created_response(category.to_dict(), "Category created successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Category creation failed: {str(e)}", 500)


@category_bp.route('/<int:category_id>', methods=['PUT'])
@token_required
def update_category(category_id):
    """Update category."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    category = Category.query.get(category_id)
    
    if not category:
        return not_found_response("Category not found")
    
    if 'category_name' in data:
        # Check if category name is taken
        existing = Category.query.filter(
            Category.category_name == data['category_name'],
            Category.id != category_id
        ).first()
        if existing:
            return error_response("Category name already exists", 400)
        category.category_name = data['category_name']
    
    try:
        db.session.commit()
        return success_response(category.to_dict(), "Category updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@category_bp.route('/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(category_id):
    """Delete category."""
    category = Category.query.get(category_id)
    
    if not category:
        return not_found_response("Category not found")
    
    # Check if category has products
    if category.products.count() > 0:
        return error_response("Cannot delete category with associated products", 400)
    
    try:
        db.session.delete(category)
        db.session.commit()
        return success_response(message="Category deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)
