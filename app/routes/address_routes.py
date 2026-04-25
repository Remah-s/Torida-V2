"""
Address Routes
==============
Routes for address management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Address, Governorate
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, validation_error_response
)
from app.utils.validators import validate_required_fields
from app.utils.auth import token_required

address_bp = Blueprint('addresses', __name__, url_prefix='/api/addresses')


@address_bp.route('', methods=['GET'])
@token_required
def get_addresses():
    """Get current user's addresses."""
    from flask import g
    user_id = g.current_user_id
    
    addresses = Address.query.filter_by(user_id=user_id).order_by(
        Address.is_default.desc(),
        Address.created_at.desc()
    ).all()
    
    return success_response([addr.to_dict() for addr in addresses])


@address_bp.route('/<int:address_id>', methods=['GET'])
@token_required
def get_address(address_id):
    """Get address by ID."""
    from flask import g
    address = Address.query.get(address_id)
    
    if not address:
        return not_found_response("Address not found")
    
    # Authorization check
    if address.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    return success_response(address.to_dict())


@address_bp.route('', methods=['POST'])
@token_required
def create_address():
    """Create a new address."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['label', 'full_address', 'gov_id']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Validate governorate
    governorate = Governorate.query.get(data['gov_id'])
    if not governorate:
        return error_response("Invalid governorate", 400)
    
    user_id = g.current_user_id
    
    try:
        # If this is the first address, make it default
        is_default = data.get('is_default', False)
        if is_default:
            # Unset other default addresses
            Address.query.filter_by(user_id=user_id, is_default=True).update(
                {'is_default': False}
            )
        
        # Check if this is the first address
        existing_count = Address.query.filter_by(user_id=user_id).count()
        if existing_count == 0:
            is_default = True
        
        address = Address(
            user_id=user_id,
            label=data['label'],
            full_address=data['full_address'],
            gov_id=data['gov_id'],
            city=data.get('city'),
            postal_code=data.get('postal_code'),
            is_default=is_default
        )
        
        db.session.add(address)
        db.session.commit()
        
        return created_response(address.to_dict(), "Address created successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Address creation failed: {str(e)}", 500)


@address_bp.route('/<int:address_id>', methods=['PUT'])
@token_required
def update_address(address_id):
    """Update address."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    address = Address.query.get(address_id)
    
    if not address:
        return not_found_response("Address not found")
    
    # Authorization check
    if address.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    if 'label' in data:
        address.label = data['label']
    
    if 'full_address' in data:
        address.full_address = data['full_address']
    
    if 'gov_id' in data:
        governorate = Governorate.query.get(data['gov_id'])
        if not governorate:
            return error_response("Invalid governorate", 400)
        address.gov_id = data['gov_id']
    
    if 'city' in data:
        address.city = data['city']
    
    if 'postal_code' in data:
        address.postal_code = data['postal_code']
    
    if 'is_default' in data and data['is_default']:
        # Unset other default addresses
        Address.query.filter_by(
            user_id=g.current_user_id, 
            is_default=True
        ).update({'is_default': False})
        address.is_default = True
    
    try:
        db.session.commit()
        return success_response(address.to_dict(), "Address updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@address_bp.route('/<int:address_id>/set-default', methods=['POST'])
@token_required
def set_default_address(address_id):
    """Set address as default."""
    from flask import g
    address = Address.query.get(address_id)
    
    if not address:
        return not_found_response("Address not found")
    
    # Authorization check
    if address.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    try:
        # Unset other default addresses
        Address.query.filter_by(
            user_id=g.current_user_id, 
            is_default=True
        ).update({'is_default': False})
        
        address.is_default = True
        db.session.commit()
        
        return success_response(message="Default address updated")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed: {str(e)}", 500)


@address_bp.route('/<int:address_id>', methods=['DELETE'])
@token_required
def delete_address(address_id):
    """Delete address."""
    from flask import g
    address = Address.query.get(address_id)
    
    if not address:
        return not_found_response("Address not found")
    
    # Authorization check
    if address.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    was_default = address.is_default
    
    try:
        db.session.delete(address)
        db.session.commit()
        
        # If deleted address was default, set another as default
        if was_default:
            next_address = Address.query.filter_by(
                user_id=g.current_user_id
            ).order_by(Address.created_at.desc()).first()
            
            if next_address:
                next_address.is_default = True
                db.session.commit()
        
        return success_response(message="Address deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)
