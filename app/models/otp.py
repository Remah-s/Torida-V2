"""
OTP Model
=========
One-Time Password for verification.
"""
from datetime import datetime
from app.database import db


class OTP(db.Model):
    """OTP model for verification codes."""
    
    __tablename__ = 'otps'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False)
    
    # Fields
    otp_code = db.Column(db.String(6), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert OTP to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'otp_code': self.otp_code,
            'is_used': self.is_used,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def is_valid(self) -> bool:
        """Check if OTP is still valid."""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def mark_used(self):
        """Mark OTP as used."""
        self.is_used = True
    
    def __repr__(self):
        return f'<OTP user={self.user_id} code={self.otp_code}>'
