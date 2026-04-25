"""
Product Sequence Model
======================
Sequence numbers for generating product codes.
"""
from app.database import db


class ProductSequence(db.Model):
    """Product sequence model for generating unique product codes."""
    
    __tablename__ = 'product_sequences'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Key
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), 
                            nullable=False, unique=True)
    
    # Fields
    sequence = db.Column(db.Integer, nullable=False, default=0)
    
    def to_dict(self):
        """Convert product sequence to dictionary."""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'sequence': self.sequence
        }
    
    def __repr__(self):
        return f'<ProductSequence category={self.category_id} seq={self.sequence}>'
