"""
User Type Model
===============
User types: Supplier (can sell), Retailer (can buy), Company (can sell).
"""
from app.database import db


class UserType(db.Model):
    """User type model defining user capabilities."""
    
    __tablename__ = 'user_types'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Fields
    type_name = db.Column(db.String(100), nullable=False, unique=True)
    can_sell = db.Column(db.Boolean, nullable=False, default=False)
    can_buy = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relationships
    users = db.relationship('User', backref='user_type', lazy='dynamic')
    
    def to_dict(self):
        """Convert user type to dictionary."""
        return {
            'id': self.id,
            'type_name': self.type_name,
            'can_sell': self.can_sell,
            'can_buy': self.can_buy
        }
    
    def __repr__(self):
        return f'<UserType {self.type_name}>'
