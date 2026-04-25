"""
Notification Service
====================
Handles creating and managing notifications.
"""
from flask import current_app
from app.database import db
from app.models import Notification, User


class NotificationService:
    """Service for notification operations."""
    
    @staticmethod
    def create_notification(
        user_id: int,
        title: str,
        body: str,
        notification_type: str = 'system',
        related_id: int = None
    ) -> Notification:
        """
        Create a new notification.
        
        Args:
            user_id: User's ID
            title: Notification title
            body: Notification body
            notification_type: Type of notification
            related_id: Related entity ID
            
        Returns:
            Created notification
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            related_id=related_id
        )
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @staticmethod
    def notify_order_update(order, status: str, user_id: int = None):
        """
        Send order update notification.
        
        Args:
            order: Order object
            status: New status
            user_id: User to notify (default: buyer)
        """
        if user_id is None:
            user_id = order.buyer_id
        
        status_messages = {
            'pending': 'Your order is pending',
            'confirmed': 'Your order has been confirmed',
            'processing': 'Your order is being processed',
            'shipped': 'Your order has been shipped',
            'out_for_delivery': 'Your order is out for delivery',
            'delivered': 'Your order has been delivered',
            'cancelled': 'Your order has been cancelled',
            'refunded': 'Your order has been refunded'
        }
        
        NotificationService.create_notification(
            user_id=user_id,
            title=f"Order #{order.id} Update",
            body=status_messages.get(status, f"Your order status has been updated to: {status}"),
            notification_type='order_update',
            related_id=order.id
        )
    
    @staticmethod
    def notify_payment_update(order, status: str):
        """
        Send payment update notification.
        
        Args:
            order: Order object
            status: Payment status
        """
        status_messages = {
            'paid': 'Payment received for your order',
            'failed': 'Payment failed for your order',
            'refunded': 'Payment has been refunded for your order'
        }
        
        NotificationService.create_notification(
            user_id=order.buyer_id,
            title=f"Payment Update - Order #{order.id}",
            body=status_messages.get(status, f"Payment status: {status}"),
            notification_type='payment_update',
            related_id=order.id
        )
    
    @staticmethod
    def notify_new_review(product, reviewer_name: str):
        """
        Notify seller of new product review.
        
        Args:
            product: Product object
            reviewer_name: Name of reviewer
        """
        NotificationService.create_notification(
            user_id=product.company_id,
            title="New Product Review",
            body=f"{reviewer_name} left a review on {product.product_name}",
            notification_type='review',
            related_id=product.id
        )
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Count of unread notifications
        """
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    @staticmethod
    def mark_all_read(user_id: int):
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: User's ID
        """
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
