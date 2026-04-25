"""
Order Routes
============
Routes for order management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Order, OrderItem, OrderStatusHistory, Cart, CartItem, Product, Address, User
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination
from app.utils.auth import token_required, buyer_required, seller_required
from app.services.notification_service import NotificationService
from app.services.email_service import EmailService

order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@order_bp.route('', methods=['GET'])
@token_required
def get_orders():
    """Get orders for current user."""
    from flask import g
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    user_id = g.current_user_id
    user = User.query.get(user_id)
    
    # Filter by role
    status = request.args.get('status')
    
    if user.can_buy():
        # Buyer - show orders they placed
        query = Order.query.filter_by(buyer_id=user_id)
    elif user.can_sell():
        # Seller - show orders for their products
        query = Order.query.filter_by(seller_id=user_id)
    else:
        query = Order.query.filter(
            db.or_(Order.buyer_id == user_id, Order.seller_id == user_id)
        )
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Order.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    orders = [order.to_dict() for order in pagination.items]
    
    return paginated_response(orders, page, per_page, pagination.total)


@order_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """Get order by ID."""
    from flask import g
    order = Order.query.get(order_id)
    
    if not order:
        return not_found_response("Order not found")
    
    # Authorization check
    user_id = g.current_user_id
    if order.buyer_id != user_id and order.seller_id != user_id:
        return error_response("Not authorized to view this order", 403)
    
    return success_response(order.to_dict_with_history())


@order_bp.route('', methods=['POST'])
@token_required
def create_order():
    """Create a new order from cart."""
    from flask import g
    data = request.get_json()
    
    user_id = g.current_user_id
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    # Check if user can buy (Retailer)
    if not user.can_buy():
        return error_response("Only retailers can place orders", 403)
    
    # Get cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart or cart.items.count() == 0:
        return error_response("Cart is empty", 400)
    
    # Validate address if provided
    address_id = data.get('address_id') if data else None
    if address_id:
        address = Address.query.get(address_id)
        if not address or address.user_id != user_id:
            return error_response("Invalid address", 400)
    
    try:
        # Group cart items by seller
        seller_items = {}
        for item in cart.items:
            product = item.product
            seller_id = product.company_id
            
            if seller_id not in seller_items:
                seller_items[seller_id] = []
            
            # Check stock
            if product.stock_quantity < item.quantity:
                return error_response(
                    f"Insufficient stock for {product.product_name}", 400
                )
            
            seller_items[seller_id].append(item)
        
        orders_created = []
        
        for seller_id, items in seller_items.items():
            # Create order
            order = Order(
                buyer_id=user_id,
                seller_id=seller_id,
                address_id=address_id,
                status='pending'
            )
            db.session.add(order)
            db.session.flush()
            
            # Add order items and reduce stock
            for cart_item in items:
                product = cart_item.product
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    price=product.price
                )
                db.session.add(order_item)
                
                # Reduce stock
                product.reduce_stock(cart_item.quantity)
            
            # Calculate total
            order.calculate_total()
            
            # Add status history
            history = OrderStatusHistory(
                order_id=order.id,
                status='pending',
                changed_by=user_id,
                note='Order created'
            )
            db.session.add(history)
            
            orders_created.append(order)
            
            # Send notification
            NotificationService.notify_order_update(order, 'pending', seller_id)
        
        # Clear cart
        CartItem.query.filter_by(cart_id=cart.id).delete()
        
        db.session.commit()
        
        # Send confirmation email
        for order in orders_created:
            EmailService.send_order_confirmation_email(
                user.email, order, user.full_name
            )
        
        return created_response(
            [order.to_dict() for order in orders_created],
            f"{len(orders_created)} order(s) created successfully"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Order creation failed: {str(e)}", 500)


@order_bp.route('/<int:order_id>/status', methods=['PUT'])
@token_required
def update_order_status(order_id):
    """Update order status."""
    from flask import g
    data = request.get_json()
    
    if not data or not data.get('status'):
        return error_response("Status is required", 400)
    
    new_status = data['status']
    
    order = Order.query.get(order_id)
    
    if not order:
        return not_found_response("Order not found")
    
    user_id = g.current_user_id
    user = User.query.get(user_id)
    
    # Authorization check
    is_seller = order.seller_id == user_id
    is_buyer = order.buyer_id == user_id
    
    if not is_seller and not is_buyer:
        return error_response("Not authorized to update this order", 403)
    
    # Validate status transition
    if not order.can_update_status(new_status):
        return error_response(
            f"Cannot change status from {order.status} to {new_status}", 400
        )
    
    # Additional authorization based on status
    if new_status == 'cancelled':
        # Both buyer and seller can cancel
        if not is_buyer and not is_seller:
            return error_response("Not authorized", 403)
    elif new_status in ['confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered']:
        # Only seller can update these
        if not is_seller:
            return error_response("Only seller can update this status", 403)
    
    try:
        old_status = order.status
        order.status = new_status
        
        # Add status history
        history = OrderStatusHistory(
            order_id=order.id,
            status=new_status,
            changed_by=user_id,
            note=data.get('note')
        )
        db.session.add(history)
        
        # Handle stock restoration for cancellation
        if new_status == 'cancelled':
            for item in order.items:
                item.product.increase_stock(item.quantity)
        
        db.session.commit()
        
        # Send notification
        NotificationService.notify_order_update(order, new_status)
        
        return success_response(order.to_dict(), "Order status updated")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@token_required
def cancel_order(order_id):
    """Cancel order."""
    from flask import g
    order = Order.query.get(order_id)
    
    if not order:
        return not_found_response("Order not found")
    
    user_id = g.current_user_id
    
    # Authorization check
    if order.buyer_id != user_id and order.seller_id != user_id:
        return error_response("Not authorized", 403)
    
    if not order.can_cancel():
        return error_response("Order cannot be cancelled", 400)
    
    try:
        # Restore stock
        for item in order.items:
            item.product.increase_stock(item.quantity)
        
        order.status = 'cancelled'
        
        history = OrderStatusHistory(
            order_id=order.id,
            status='cancelled',
            changed_by=user_id,
            note='Order cancelled'
        )
        db.session.add(history)
        
        db.session.commit()
        
        NotificationService.notify_order_update(order, 'cancelled')
        
        return success_response(message="Order cancelled successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Cancel failed: {str(e)}", 500)


@order_bp.route('/<int:order_id>/items', methods=['GET'])
@token_required
def get_order_items(order_id):
    """Get items for an order."""
    from flask import g
    order = Order.query.get(order_id)
    
    if not order:
        return not_found_response("Order not found")
    
    user_id = g.current_user_id
    if order.buyer_id != user_id and order.seller_id != user_id:
        return error_response("Not authorized", 403)
    
    items = [item.to_dict() for item in order.items]
    
    return success_response(items)


@order_bp.route('/<int:order_id>/history', methods=['GET'])
@token_required
def get_order_history(order_id):
    """Get status history for an order."""
    from flask import g
    order = Order.query.get(order_id)
    
    if not order:
        return not_found_response("Order not found")
    
    user_id = g.current_user_id
    if order.buyer_id != user_id and order.seller_id != user_id:
        return error_response("Not authorized", 403)
    
    history = [h.to_dict() for h in order.status_history.order_by(
        OrderStatusHistory.changed_at.desc()
    )]
    
    return success_response(history)
