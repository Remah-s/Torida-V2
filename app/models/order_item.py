"""
Order Item Model
================
Individual items within an order.
"""
from app.database import db


class OrderItem(db.Model):
    """Order item model."""
    
    __tablename__ = 'order_items'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), 
                         nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), 
                           nullable=False)
    
    # Fields
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price snapshot at time of order
    
    def to_dict(self):
        """Convert order item to dictionary."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'product_image': self.product.get_primary_image() if self.product else None,
            'quantity': self.quantity,
            'price': float(self.price) if self.price else None,
            'subtotal': float(self.price) * self.quantity if self.price else None
        }
    
    def __repr__(self):
        return f'<OrderItem {self.id} order={self.order_id}>'
