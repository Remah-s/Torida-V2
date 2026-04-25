"""
Order Status History Model
==========================
History of order status changes.
"""
from datetime import datetime
from app.database import db


class OrderStatusHistory(db.Model):
    """Order status history model."""
    
    __tablename__ = 'order_status_history'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), 
                         nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    
    # Fields
    status = db.Column(db.Enum(
        'pending', 'confirmed', 'processing', 'shipped',
        'out_for_delivery', 'delivered', 'cancelled', 'refunded',
        name='history_status'
    ), nullable=False)
    note = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    changer = db.relationship('User', backref='status_changes')
    
    def to_dict(self):
        """Convert status history to dictionary."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'status': self.status,
            'changed_by': self.changed_by,
            'changed_by_name': self.changer.full_name if self.changer else None,
            'note': self.note,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }
    
    def __repr__(self):
        return f'<OrderStatusHistory order={self.order_id} status={self.status}>'
