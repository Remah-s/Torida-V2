"""
Address Model
=============
User shipping/billing addresses.
"""
from datetime import datetime
from app.database import db


class Address(db.Model):
    """Address model for user shipping/billing addresses."""
    
    __tablename__ = 'addresses'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False)
    gov_id = db.Column(db.Integer, db.ForeignKey('governorates.id', ondelete='RESTRICT'), 
                       nullable=False)
    
    # Fields
    label = db.Column(db.String(50), nullable=False)  # e.g., 'Home', 'Office', 'Warehouse'
    full_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='shipping_address', lazy='dynamic')
    
    def to_dict(self):
        """Convert address to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'label': self.label,
            'full_address': self.full_address,
            'gov_id': self.gov_id,
            'gov_name': self.governorate.gov_name if self.governorate else None,
            'city': self.city,
            'postal_code': self.postal_code,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Address {self.label} - {self.full_address}>'
