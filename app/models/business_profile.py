"""
Business Profile Model
======================
Business information for suppliers and companies.
"""
from datetime import datetime
from app.database import db
from app.utils.helpers import build_public_url


class BusinessProfile(db.Model):
    """Business profile model for suppliers and companies."""
    
    __tablename__ = 'business_profiles'
    
    # Primary Key (also Foreign Key to users)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        primary_key=True)
    
    # Fields
    business_name = db.Column(db.String(150), nullable=False)
    tax_number = db.Column(db.String(50), unique=True)
    commercial_register = db.Column(db.String(50), unique=True)
    address = db.Column(db.String(255), nullable=False)
    logo_url = db.Column(db.String(500))
    cover_image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert business profile to dictionary."""
        return {
            'user_id': self.user_id,
            'business_name': self.business_name,
            'tax_number': self.tax_number,
            'commercial_register': self.commercial_register,
            'address': self.address,
            'logo_url': build_public_url(self.logo_url),
            'cover_image_url': build_public_url(self.cover_image_url),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<BusinessProfile {self.business_name}>'
