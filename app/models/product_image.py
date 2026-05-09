"""
Product Image Model
===================
Product images for marketplace products.
"""
from datetime import datetime
from app.database import db
from app.utils.helpers import build_public_url


class ProductImage(db.Model):
    """Product image model."""
    
    __tablename__ = 'product_images'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Key
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), 
                           nullable=False)
    
    # Fields
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert product image to dictionary."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'image_url': build_public_url(self.image_url),
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ProductImage {self.id} product={self.product_id}>'
