"""
User Model
==========
Main user model for all user types (Supplier, Retailer, Company).
"""
from datetime import datetime
from app.database import db


class User(db.Model):
    """User model for all user types."""
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # Fields
    code = db.Column(db.String(10), unique=True)
    custom_id = db.Column(db.String(20), unique=True)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(60), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    type_id = db.Column(db.Integer, db.ForeignKey('user_types.id', ondelete='RESTRICT'), 
                        nullable=False)
    gov_id = db.Column(db.Integer, db.ForeignKey('governorates.id', ondelete='RESTRICT'), 
                       nullable=False)
    
    # Relationships
    user_roles = db.relationship('UserRole', backref='user', lazy='dynamic', 
                                  cascade='all, delete-orphan')
    business_profile = db.relationship('BusinessProfile', backref='user', uselist=False,
                                        cascade='all, delete-orphan')
    otps = db.relationship('OTP', backref='user', lazy='dynamic', 
                           cascade='all, delete-orphan')
    addresses = db.relationship('Address', backref='user', lazy='dynamic', 
                                cascade='all, delete-orphan')
    products = db.relationship('Product', backref='seller', lazy='dynamic',
                               foreign_keys='Product.company_id',
                               cascade='all, delete-orphan')
    buyer_orders = db.relationship('Order', backref='buyer', lazy='dynamic',
                                    foreign_keys='Order.buyer_id',
                                    cascade='all, delete-orphan')
    seller_orders = db.relationship('Order', backref='seller', lazy='dynamic',
                                     foreign_keys='Order.seller_id',
                                     cascade='all, delete-orphan')
    reviews = db.relationship('ProductReview', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')
    cart = db.relationship('Cart', backref='user', uselist=False,
                           cascade='all, delete-orphan')
    wishlist_items = db.relationship('Wishlist', backref='user', lazy='dynamic',
                                      cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic',
                                     cascade='all, delete-orphan')
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'code': self.code,
            'custom_id': self.custom_id,
            'type_id': self.type_id,
            'type_name': self.user_type.type_name if self.user_type else None,
            'gov_id': self.gov_id,
            'gov_name': self.governorate.gov_name if self.governorate else None,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data['roles'] = [ur.role.to_dict() for ur in self.user_roles]
            data['business_profile'] = self.business_profile.to_dict() if self.business_profile else None
        
        return data
    
    def to_public_dict(self):
        """Convert user to public dictionary (limited info)."""
        return {
            'id': self.id,
            'custom_id': self.custom_id,
            'full_name': self.full_name,
            'type_name': self.user_type.type_name if self.user_type else None,
            'gov_name': self.governorate.gov_name if self.governorate else None
        }
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        from app.models import Role, UserRole
        role = Role.query.filter_by(role_name=role_name).first()
        if role:
            return UserRole.query.filter_by(user_id=self.id, role_id=role.id).first() is not None
        return False
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission through any role."""
        from app.models import Permission, RolePermission, UserRole
        permission = Permission.query.filter_by(permission_name=permission_name).first()
        if permission:
            user_role_ids = [ur.role_id for ur in self.user_roles]
            return RolePermission.query.filter(
                RolePermission.role_id.in_(user_role_ids),
                RolePermission.permission_id == permission.id
            ).first() is not None
        return False
    
    def can_sell(self) -> bool:
        """Check if user can sell products."""
        return self.user_type.can_sell if self.user_type else False
    
    def can_buy(self) -> bool:
        """Check if user can buy products."""
        return self.user_type.can_buy if self.user_type else False
    
    def __repr__(self):
        return f'<User {self.custom_id} - {self.full_name}>'
