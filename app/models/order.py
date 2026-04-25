"""
Order Model
===========
Orders placed by retailers (buyers) to suppliers/companies (sellers).
"""
from datetime import datetime
from app.database import db


class Order(db.Model):
    """Order model for marketplace orders."""
    
    __tablename__ = 'orders'
    
    # Order status enum
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        STATUS_PENDING, STATUS_CONFIRMED, STATUS_PROCESSING,
        STATUS_SHIPPED, STATUS_OUT_FOR_DELIVERY, STATUS_DELIVERED,
        STATUS_CANCELLED, STATUS_REFUNDED
    ]
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                         nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                          nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id', ondelete='SET NULL'))
    
    # Fields
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    status = db.Column(db.Enum(*STATUS_CHOICES, name='order_status'), 
                       nullable=False, default=STATUS_PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic',
                            cascade='all, delete-orphan')
    status_history = db.relationship('OrderStatusHistory', backref='order', lazy='dynamic',
                                      cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False,
                              cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert order to dictionary."""
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'buyer_name': self.buyer.full_name if self.buyer else None,
            'seller_id': self.seller_id,
            'seller_name': self.seller.full_name if self.seller else None,
            'address_id': self.address_id,
            'shipping_address': self.shipping_address.to_dict() if self.shipping_address else None,
            'total_price': float(self.total_price) if self.total_price else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_with_items(self):
        """Convert order to dictionary with items."""
        data = self.to_dict()
        data['items'] = [item.to_dict() for item in self.items]
        data['payment'] = self.payment.to_dict() if self.payment else None
        return data
    
    def to_dict_with_history(self):
        """Convert order to dictionary with status history."""
        data = self.to_dict_with_items()
        data['status_history'] = [h.to_dict() for h in self.status_history.order_by(
            OrderStatusHistory.changed_at.desc()
        )]
        return data
    
    def calculate_total(self):
        """Calculate total price from items."""
        total = sum(float(item.price) * item.quantity for item in self.items)
        self.total_price = total
        return total
    
    def can_cancel(self) -> bool:
        """Check if order can be cancelled."""
        return self.status in [self.STATUS_PENDING, self.STATUS_CONFIRMED]
    
    def can_update_status(self, new_status: str) -> bool:
        """Check if status can be updated to new status."""
        status_flow = {
            self.STATUS_PENDING: [self.STATUS_CONFIRMED, self.STATUS_CANCELLED],
            self.STATUS_CONFIRMED: [self.STATUS_PROCESSING, self.STATUS_CANCELLED],
            self.STATUS_PROCESSING: [self.STATUS_SHIPPED, self.STATUS_CANCELLED],
            self.STATUS_SHIPPED: [self.STATUS_OUT_FOR_DELIVERY],
            self.STATUS_OUT_FOR_DELIVERY: [self.STATUS_DELIVERED],
            self.STATUS_DELIVERED: [self.STATUS_REFUNDED],
            self.STATUS_CANCELLED: [],
            self.STATUS_REFUNDED: []
        }
        return new_status in status_flow.get(self.status, [])
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'
