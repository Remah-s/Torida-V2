"""
Governorate Model
=================
Egyptian governorates (provinces).
"""
from app.database import db


class Governorate(db.Model):
    """Governorate model representing Egyptian provinces."""
    
    __tablename__ = 'governorates'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Fields
    gov_name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationships
    users = db.relationship('User', backref='governorate', lazy='dynamic')
    addresses = db.relationship('Address', backref='governorate', lazy='dynamic')
    
    def to_dict(self):
        """Convert governorate to dictionary."""
        return {
            'id': self.id,
            'gov_name': self.gov_name
        }
    
    def __repr__(self):
        return f'<Governorate {self.gov_name}>'
