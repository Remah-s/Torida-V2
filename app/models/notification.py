"""
Notification Model
==================
User notifications.
"""
from datetime import datetime
from app.database import db


class Notification(db.Model):
    """Notification model."""
    
    __tablename__ = 'notifications'
    
    # Notification types
    TYPE_ORDER_UPDATE = 'order_update'
    TYPE_PAYMENT_UPDATE = 'payment_update'
    TYPE_DELIVERY_UPDATE = 'delivery_update'
    TYPE_REVIEW = 'review'
    TYPE_SYSTEM = 'system'
    TYPE_PROMO = 'promo'
    
    TYPE_CHOICES = [
        TYPE_ORDER_UPDATE, TYPE_PAYMENT_UPDATE, TYPE_DELIVERY_UPDATE,
        TYPE_REVIEW, TYPE_SYSTEM, TYPE_PROMO
    ]
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False)
    
    # Fields
    type = db.Column(db.Enum(*TYPE_CHOICES, name='notification_type'), 
                     nullable=False, default=TYPE_SYSTEM)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    related_id = db.Column(db.Integer)  # Flexible: order_id, product_id, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'body': self.body,
            'is_read': self.is_read,
            'related_id': self.related_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def mark_read(self):
        """Mark notification as read."""
        self.is_read = True
    
    def __repr__(self):
        return f'<Notification {self.id} user={self.user_id} type={self.type}>'
