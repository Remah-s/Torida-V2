"""
Payment Routes
==============
Routes for payment management.
"""
from flask import Blueprint, request
from datetime import datetime

from app.database import db
from app.models import Payment, Order, User
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, validation_error_response
)
from app.utils.validators import validate_required_fields
from app.utils.auth import token_required
from app.services.notification_service import NotificationService

payment_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@payment_bp.route('/order/<int:order_id>', methods=['GET'])
@token_required
def get_payment_by_order(order_id):
    """Get payment for an order."""
    from flask import g
    order = Order.query.get(order_id)
    
    if not order:
        return not_found_response("Order not found")
    
    user_id = g.current_user_id
    if order.buyer_id != user_id and order.seller_id != user_id:
        return error_response("Not authorized", 403)
    
    payment = Payment.query.filter_by(order_id=order_id).first()
    
    if not payment:
        return not_found_response("Payment not found")
    
    return success_response(payment.to_dict())


@payment_bp.route('', methods=['POST'])
@token_required
def create_payment():
    """Create payment for an order."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['order_id', 'method']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    order = Order.query.get(data['order_id'])
    
    if not order:
        return not_found_response("Order not found")
    
    # Only buyer can make payment
    if order.buyer_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    # Check if payment already exists
    existing = Payment.query.filter_by(order_id=data['order_id']).first()
    if existing:
        return error_response("Payment already exists for this order", 400)
    
    try:
        payment = Payment(
            order_id=data['order_id'],
            amount=order.total_price,
            method=data['method'],
            status='unpaid'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return created_response(payment.to_dict(), "Payment created")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Payment creation failed: {str(e)}", 500)


@payment_bp.route('/<int:payment_id>/pay', methods=['POST'])
@token_required
def process_payment(payment_id):
    """Process payment (simulate payment processing)."""
    from flask import g
    data = request.get_json()
    
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return not_found_response("Payment not found")
    
    order = payment.order
    
    # Only buyer can pay
    if order.buyer_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    if payment.status == 'paid':
        return error_response("Payment already processed", 400)
    
    if payment.status == 'refunded':
        return error_response("Payment has been refunded", 400)
    
    try:
        # Simulate payment processing
        # In real application, integrate with payment gateway
        
        transaction_id = data.get('transaction_id') if data else None
        if not transaction_id:
            # Generate mock transaction ID
            transaction_id = f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{payment_id}"
        
        payment.mark_paid(transaction_id)
        
        # Update order status if pending
        if order.status == 'pending':
            order.status = 'confirmed'
        
        db.session.commit()
        
        NotificationService.notify_payment_update(order, 'paid')
        
        return success_response(payment.to_dict(), "Payment processed successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Payment processing failed: {str(e)}", 500)


@payment_bp.route('/<int:payment_id>/refund', methods=['POST'])
@token_required
def refund_payment(payment_id):
    """Refund payment."""
    from flask import g
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return not_found_response("Payment not found")
    
    order = payment.order
    
    # Only seller or admin can refund
    user = User.query.get(g.current_user_id)
    if order.seller_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    if payment.status != 'paid':
        return error_response("Only paid payments can be refunded", 400)
    
    try:
        payment.mark_refunded()
        order.status = 'refunded'
        
        db.session.commit()
        
        NotificationService.notify_payment_update(order, 'refunded')
        
        return success_response(payment.to_dict(), "Payment refunded")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Refund failed: {str(e)}", 500)
