"""
Cart Model
==========
Shopping cart for retailers.
"""
from datetime import datetime
from app.database import db


class Cart(db.Model):
    """Cart model for retailers."""
    
    __tablename__ = 'carts'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False, unique=True)
    
    # Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy='dynamic',
                            cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert cart to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items],
            'total_items': self.items.count(),
            'total_price': self.calculate_total(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_total(self):
        """Calculate total price of cart items."""
        total = 0
        for item in self.items:
            if item.product and item.product.price:
                total += float(item.product.price) * item.quantity
        return round(total, 2)
    
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    def clear(self):
        """Clear all items from cart."""
        for item in self.items:
            db.session.delete(item)
    
    def __repr__(self):
        return f'<Cart {self.id} user={self.user_id}>'
