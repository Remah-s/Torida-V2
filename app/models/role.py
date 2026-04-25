"""
Role Model
==========
User roles for access control.
"""
from datetime import datetime
from app.database import db


class Role(db.Model):
    """Role model for user access control."""
    
    __tablename__ = 'roles'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Fields
    custom_id = db.Column(db.String(20), unique=True)
    role_name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_roles = db.relationship('UserRole', backref='role', lazy='dynamic', 
                                  cascade='all, delete-orphan')
    role_permissions = db.relationship('RolePermission', backref='role', lazy='dynamic',
                                        cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert role to dictionary."""
        return {
            'id': self.id,
            'custom_id': self.custom_id,
            'role_name': self.role_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_with_permissions(self):
        """Convert role to dictionary with permissions."""
        data = self.to_dict()
        data['permissions'] = [rp.permission.to_dict() for rp in self.role_permissions]
        return data
    
    def __repr__(self):
        return f'<Role {self.role_name}>'
