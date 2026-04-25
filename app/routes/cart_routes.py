"""
Cart Routes
===========
Routes for shopping cart management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Cart, CartItem, Product, User
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, validation_error_response
)
from app.utils.validators import validate_quantity
from app.utils.auth import token_required, buyer_required

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


@cart_bp.route('', methods=['GET'])
@token_required
def get_cart():
    """Get current user's cart."""
    from flask import g
    user_id = g.current_user_id
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return success_response({'items': [], 'total_items': 0, 'total_price': 0})
    
    return success_response(cart.to_dict())


@cart_bp.route('/items', methods=['POST'])
@token_required
def add_to_cart():
    """Add item to cart."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    if not data.get('product_id'):
        return error_response("Product ID is required", 400)
    
    quantity = data.get('quantity', 1)
    is_valid, error_msg = validate_quantity(quantity)
    if not is_valid:
        return error_response(error_msg, 400)
    
    if quantity < 1:
        return error_response("Quantity must be at least 1", 400)
    
    # Check product exists and is active
    product = Product.query.get(data['product_id'])
    if not product:
        return not_found_response("Product not found")
    
    if not product.is_active:
        return error_response("Product is not available", 400)
    
    # Check stock
    if product.stock_quantity < quantity:
        return error_response("Insufficient stock", 400)
    
    # Get or create cart
    user_id = g.current_user_id
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.flush()
    
    # Check if product already in cart
    existing_item = CartItem.query.filter_by(
        cart_id=cart.id, 
        product_id=data['product_id']
    ).first()
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + quantity
        if product.stock_quantity < new_quantity:
            return error_response("Insufficient stock", 400)
        existing_item.quantity = new_quantity
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=data['product_id'],
            quantity=quantity
        )
        db.session.add(cart_item)
    
    try:
        db.session.commit()
        return success_response(cart.to_dict(), "Item added to cart")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to add item: {str(e)}", 500)


@cart_bp.route('/items/<int:item_id>', methods=['PUT'])
@token_required
def update_cart_item(item_id):
    """Update cart item quantity."""
    from flask import g
    data = request.get_json()
    
    if not data or 'quantity' not in data:
        return error_response("Quantity is required", 400)
    
    quantity = data['quantity']
    is_valid, error_msg = validate_quantity(quantity)
    if not is_valid:
        return error_response(error_msg, 400)
    
    if quantity < 1:
        return error_response("Quantity must be at least 1", 400)
    
    # Get cart item
    user_id = g.current_user_id
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return not_found_response("Cart not found")
    
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    
    if not cart_item:
        return not_found_response("Cart item not found")
    
    # Check stock
    if cart_item.product.stock_quantity < quantity:
        return error_response("Insufficient stock", 400)
    
    try:
        cart_item.quantity = quantity
        db.session.commit()
        return success_response(cart.to_dict(), "Cart updated")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@cart_bp.route('/items/<int:item_id>', methods=['DELETE'])
@token_required
def remove_cart_item(item_id):
    """Remove item from cart."""
    from flask import g
    user_id = g.current_user_id
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return not_found_response("Cart not found")
    
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    
    if not cart_item:
        return not_found_response("Cart item not found")
    
    try:
        db.session.delete(cart_item)
        db.session.commit()
        return success_response(cart.to_dict(), "Item removed from cart")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Remove failed: {str(e)}", 500)


@cart_bp.route('', methods=['DELETE'])
@token_required
def clear_cart():
    """Clear all items from cart."""
    from flask import g
    user_id = g.current_user_id
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return success_response(message="Cart is already empty")
    
    try:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        return success_response(message="Cart cleared successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Clear failed: {str(e)}", 500)
