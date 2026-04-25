"""
User Role Model
===============
Many-to-many relationship between users and roles.
"""
from app.database import db


class UserRole(db.Model):
    """User-Role association model."""
    
    __tablename__ = 'user_roles'
    
    # Composite Primary Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), 
                        primary_key=True)
    
    def to_dict(self):
        """Convert user role to dictionary."""
        return {
            'user_id': self.user_id,
            'role_id': self.role_id
        }
    
    def __repr__(self):
        return f'<UserRole user={self.user_id} role={self.role_id}>'
