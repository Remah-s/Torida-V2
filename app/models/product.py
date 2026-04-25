"""
Product Model
=============
Products listed by suppliers and companies.
"""
from datetime import datetime
from app.database import db


class Product(db.Model):
    """Product model for marketplace products."""
    
    __tablename__ = 'products'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Fields
    code = db.Column(db.String(6), unique=True)
    custom_id = db.Column(db.String(20), unique=True)
    product_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    company_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                           nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), 
                            nullable=False)
    
    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy='dynamic',
                             cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic',
                                  cascade='all, delete-orphan')
    reviews = db.relationship('ProductReview', backref='product', lazy='dynamic',
                              cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic',
                                 cascade='all, delete-orphan')
    wishlist_items = db.relationship('Wishlist', backref='product', lazy='dynamic',
                                     cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'code': self.code,
            'custom_id': self.custom_id,
            'company_id': self.company_id,
            'seller_name': self.seller.full_name if self.seller else None,
            'seller_type': self.seller.user_type.type_name if self.seller and self.seller.user_type else None,
            'category_id': self.category_id,
            'category_name': self.category.category_name if self.category else None,
            'product_name': self.product_name,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'stock_quantity': self.stock_quantity,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_with_images(self):
        """Convert product to dictionary with images."""
        data = self.to_dict()
        data['images'] = [img.to_dict() for img in self.images]
        data['primary_image'] = self.get_primary_image()
        return data
    
    def to_dict_with_reviews(self):
        """Convert product to dictionary with reviews."""
        data = self.to_dict_with_images()
        reviews = self.reviews.limit(10).all()
        data['reviews'] = [review.to_dict() for review in reviews]
        data['average_rating'] = self.get_average_rating()
        data['review_count'] = self.reviews.count()
        return data
    
    def get_primary_image(self):
        """Get the primary image URL."""
        primary = self.images.filter_by(is_primary=True).first()
        if primary:
            return primary.image_url
        first_image = self.images.first()
        return first_image.image_url if first_image else None
    
    def get_average_rating(self):
        """Calculate average rating."""
        from sqlalchemy import func
        result = db.session.query(func.avg(ProductReview.rating)).filter(
            ProductReview.product_id == self.id
        ).scalar()
        return round(float(result), 1) if result else None
    
    def is_in_stock(self, quantity=1) -> bool:
        """Check if product has enough stock."""
        return self.stock_quantity >= quantity and self.is_active
    
    def reduce_stock(self, quantity: int):
        """Reduce stock quantity."""
        self.stock_quantity -= quantity
    
    def increase_stock(self, quantity: int):
        """Increase stock quantity."""
        self.stock_quantity += quantity
    
    def __repr__(self):
        return f'<Product {self.custom_id} - {self.product_name}>'
