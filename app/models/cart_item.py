"""
Cart Item Model
===============
Items in shopping cart.
"""
from datetime import datetime
from app.database import db


class CartItem(db.Model):
    """Cart item model."""
    
    __tablename__ = 'cart_items'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id', ondelete='CASCADE'), 
                        nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), 
                           nullable=False)
    
    # Fields
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint (no duplicate products in cart)
    __table_args__ = (
        db.UniqueConstraint('cart_id', 'product_id', name='uq_cart_product'),
    )
    
    def to_dict(self):
        """Convert cart item to dictionary."""
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'product': self.product.to_dict_with_images() if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.product.price) if self.product and self.product.price else None,
            'subtotal': float(self.product.price) * self.quantity if self.product and self.product.price else None,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }
    
    def __repr__(self):
        return f'<CartItem {self.id} cart={self.cart_id} product={self.product_id}>'
