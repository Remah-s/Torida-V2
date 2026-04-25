"""
Payment Model
=============
Payment information for orders.
"""
from datetime import datetime
from app.database import db


class Payment(db.Model):
    """Payment model for order payments."""
    
    __tablename__ = 'payments'
    
    # Payment method enum
    METHOD_CASH = 'cash'
    METHOD_CREDIT_CARD = 'credit_card'
    METHOD_BANK_TRANSFER = 'bank_transfer'
    METHOD_WALLET = 'wallet'
    
    METHOD_CHOICES = [METHOD_CASH, METHOD_CREDIT_CARD, METHOD_BANK_TRANSFER, METHOD_WALLET]
    
    # Payment status enum
    STATUS_UNPAID = 'unpaid'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    
    STATUS_CHOICES = [STATUS_UNPAID, STATUS_PAID, STATUS_FAILED, STATUS_REFUNDED]
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Key (One-to-One with orders)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), 
                         nullable=False, unique=True)
    
    # Fields
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.Enum(*METHOD_CHOICES, name='payment_method'), 
                       nullable=False, default=METHOD_CASH)
    status = db.Column(db.Enum(*STATUS_CHOICES, name='payment_status'), 
                       nullable=False, default=STATUS_UNPAID)
    transaction_id = db.Column(db.String(100), unique=True)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert payment to dictionary."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': float(self.amount) if self.amount else None,
            'method': self.method,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def mark_paid(self, transaction_id: str = None):
        """Mark payment as paid."""
        self.status = self.STATUS_PAID
        self.paid_at = datetime.utcnow()
        if transaction_id:
            self.transaction_id = transaction_id
    
    def mark_failed(self):
        """Mark payment as failed."""
        self.status = self.STATUS_FAILED
    
    def mark_refunded(self):
        """Mark payment as refunded."""
        self.status = self.STATUS_REFUNDED
    
    def __repr__(self):
        return f'<Payment {self.id} order={self.order_id} status={self.status}>'
