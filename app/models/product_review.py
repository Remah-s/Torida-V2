"""
Product Review Model
====================
Reviews and ratings for products.
"""
from datetime import datetime
from app.database import db


class ProductReview(db.Model):
    """Product review model."""
    
    __tablename__ = 'product_reviews'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), 
                           nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False)
    
    # Fields
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint (one review per user per product)
    __table_args__ = (
        db.UniqueConstraint('product_id', 'user_id', name='uq_product_user_review'),
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='ck_rating_range')
    )
    
    def to_dict(self):
        """Convert review to dictionary."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ProductReview {self.id} product={self.product_id} rating={self.rating}>'
