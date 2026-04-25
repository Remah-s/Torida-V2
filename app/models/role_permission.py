"""
Role Permission Model
=====================
Many-to-many relationship between roles and permissions.
"""
from app.database import db


class RolePermission(db.Model):
    """Role-Permission association model."""
    
    __tablename__ = 'role_permissions'
    
    # Composite Primary Key
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), 
                        primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id', ondelete='CASCADE'), 
                               primary_key=True)
    
    def to_dict(self):
        """Convert role permission to dictionary."""
        return {
            'role_id': self.role_id,
            'permission_id': self.permission_id
        }
    
    def __repr__(self):
        return f'<RolePermission role={self.role_id} permission={self.permission_id}>'
