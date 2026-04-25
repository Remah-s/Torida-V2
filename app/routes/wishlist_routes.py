"""
Wishlist Routes
===============
Routes for wishlist management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Wishlist, Product
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response
)
from app.utils.validators import validate_pagination
from app.utils.auth import token_required

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/api/wishlist')


@wishlist_bp.route('', methods=['GET'])
@token_required
def get_wishlist():
    """Get current user's wishlist."""
    from flask import g
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    user_id = g.current_user_id
    
    query = Wishlist.query.filter_by(user_id=user_id).order_by(Wishlist.added_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = [item.to_dict() for item in pagination.items]
    
    return paginated_response(items, page, per_page, pagination.total)


@wishlist_bp.route('', methods=['POST'])
@token_required
def add_to_wishlist():
    """Add product to wishlist."""
    from flask import g
    data = request.get_json()
    
    if not data or not data.get('product_id'):
        return error_response("Product ID is required", 400)
    
    # Check product exists
    product = Product.query.get(data['product_id'])
    if not product:
        return not_found_response("Product not found")
    
    user_id = g.current_user_id
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(
        user_id=user_id, 
        product_id=data['product_id']
    ).first()
    
    if existing:
        return error_response("Product already in wishlist", 400)
    
    try:
        wishlist_item = Wishlist(
            user_id=user_id,
            product_id=data['product_id']
        )
        db.session.add(wishlist_item)
        db.session.commit()
        
        return created_response(wishlist_item.to_dict(), "Product added to wishlist")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to add to wishlist: {str(e)}", 500)


@wishlist_bp.route('/<int:product_id>', methods=['DELETE'])
@token_required
def remove_from_wishlist(product_id):
    """Remove product from wishlist."""
    from flask import g
    user_id = g.current_user_id
    
    wishlist_item = Wishlist.query.filter_by(
        user_id=user_id, 
        product_id=product_id
    ).first()
    
    if not wishlist_item:
        return not_found_response("Product not in wishlist")
    
    try:
        db.session.delete(wishlist_item)
        db.session.commit()
        return success_response(message="Product removed from wishlist")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Remove failed: {str(e)}", 500)


@wishlist_bp.route('/check/<int:product_id>', methods=['GET'])
@token_required
def check_wishlist(product_id):
    """Check if product is in wishlist."""
    from flask import g
    user_id = g.current_user_id
    
    exists = Wishlist.query.filter_by(
        user_id=user_id, 
        product_id=product_id
    ).first() is not None
    
    return success_response({'in_wishlist': exists})
