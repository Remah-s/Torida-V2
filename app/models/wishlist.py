"""
Wishlist Model
==============
User wishlist for products.
"""
from datetime import datetime
from app.database import db


class Wishlist(db.Model):
    """Wishlist model."""
    
    __tablename__ = 'wishlists'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), 
                           nullable=False)
    
    # Fields
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='uq_user_product_wishlist'),
    )
    
    def to_dict(self):
        """Convert wishlist item to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product': self.product.to_dict_with_images() if self.product else None,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }
    
    def __repr__(self):
        return f'<Wishlist {self.id} user={self.user_id} product={self.product_id}>'
