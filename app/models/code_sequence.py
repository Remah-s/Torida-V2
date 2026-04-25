"""
Code Sequence Model
===================
Sequence numbers for generating user codes.
"""
from app.database import db


class CodeSequence(db.Model):
    """Code sequence model for generating unique user codes."""
    
    __tablename__ = 'code_sequences'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Foreign Keys
    type_id = db.Column(db.Integer, db.ForeignKey('user_types.id', ondelete='CASCADE'), 
                        nullable=False)
    gov_id = db.Column(db.Integer, db.ForeignKey('governorates.id', ondelete='CASCADE'), 
                       nullable=False)
    
    # Fields
    sequence = db.Column(db.Integer, nullable=False, default=0)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('type_id', 'gov_id', name='uq_type_gov'),
    )
    
    def to_dict(self):
        """Convert code sequence to dictionary."""
        return {
            'id': self.id,
            'type_id': self.type_id,
            'gov_id': self.gov_id,
            'sequence': self.sequence
        }
    
    def __repr__(self):
        return f'<CodeSequence type={self.type_id} gov={self.gov_id} seq={self.sequence}>'
