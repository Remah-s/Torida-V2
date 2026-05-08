"""
Role Sequence Model
===================
Sequence counter for generating role custom IDs (ROL-XXXXX).
The MySQL trigger `trg_roles_custom_id` reads and increments
the counter in row id=1 on every INSERT into the roles table.
"""
from app.database import db


class RoleSequence(db.Model):
    """Role sequence model for generating unique role custom IDs."""
    
    __tablename__ = 'role_sequences'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Fields
    sequence = db.Column(db.Integer, nullable=False, default=0)
    
    def to_dict(self):
        """Convert role sequence to dictionary."""
        return {
            'id': self.id,
            'sequence': self.sequence
        }
    
    def __repr__(self):
        return f'<RoleSequence id={self.id} seq={self.sequence}>'
