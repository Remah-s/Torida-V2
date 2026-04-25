"""
Permission Model
================
Permissions for role-based access control.
"""
from app.database import db


class Permission(db.Model):
    """Permission model for access control."""
    
    __tablename__ = 'permissions'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Fields
    permission_name = db.Column(db.String(150), nullable=False, unique=True)
    
    # Relationships
    role_permissions = db.relationship('RolePermission', backref='permission', lazy='dynamic',
                                        cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert permission to dictionary."""
        return {
            'id': self.id,
            'permission_name': self.permission_name
        }
    
    def __repr__(self):
        return f'<Permission {self.permission_name}>'
