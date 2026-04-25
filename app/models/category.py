"""
Category Model
==============
Product categories.
"""
from datetime import datetime
from app.database import db


class Category(db.Model):
    """Category model for product categorization."""
    
    __tablename__ = 'categories'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Fields
    custom_id = db.Column(db.String(20), unique=True)
    category_name = db.Column(db.String(150), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    product_sequence = db.relationship('ProductSequence', backref='category', uselist=False)
    
    def to_dict(self):
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'custom_id': self.custom_id,
            'category_name': self.category_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_with_product_count(self):
        """Convert category to dictionary with product count."""
        data = self.to_dict()
        data['product_count'] = self.products.filter_by(is_active=True).count()
        return data
    
    def __repr__(self):
        return f'<Category {self.category_name}>'
