"""
Governorate Routes
==================
Routes for governorate management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Governorate
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination
from app.utils.auth import token_required

governorate_bp = Blueprint('governorates', __name__, url_prefix='/api/governorates')


@governorate_bp.route('', methods=['GET'])
def get_governorates():
    """Get all governorates."""
    governorates = Governorate.query.order_by(Governorate.gov_name).all()
    
    return success_response([gov.to_dict() for gov in governorates])


@governorate_bp.route('/<int:governorate_id>', methods=['GET'])
def get_governorate(governorate_id):
    """Get governorate by ID."""
    governorate = Governorate.query.get(governorate_id)
    
    if not governorate:
        return not_found_response("Governorate not found")
    
    return success_response(governorate.to_dict())


@governorate_bp.route('', methods=['POST'])
@token_required
def create_governorate():
    """Create a new governorate."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['gov_name']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Check if governorate name already exists
    if Governorate.query.filter_by(gov_name=data['gov_name']).first():
        return error_response("Governorate name already exists", 400)
    
    try:
        governorate = Governorate(gov_name=data['gov_name'])
        db.session.add(governorate)
        db.session.commit()
        
        return created_response(governorate.to_dict(), "Governorate created successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Governorate creation failed: {str(e)}", 500)


@governorate_bp.route('/<int:governorate_id>', methods=['PUT'])
@token_required
def update_governorate(governorate_id):
    """Update governorate."""
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    governorate = Governorate.query.get(governorate_id)
    
    if not governorate:
        return not_found_response("Governorate not found")
    
    if 'gov_name' in data:
        # Check if governorate name is taken
        existing = Governorate.query.filter(
            Governorate.gov_name == data['gov_name'],
            Governorate.id != governorate_id
        ).first()
        if existing:
            return error_response("Governorate name already exists", 400)
        governorate.gov_name = data['gov_name']
    
    try:
        db.session.commit()
        return success_response(governorate.to_dict(), "Governorate updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@governorate_bp.route('/<int:governorate_id>', methods=['DELETE'])
@token_required
def delete_governorate(governorate_id):
    """Delete governorate."""
    governorate = Governorate.query.get(governorate_id)
    
    if not governorate:
        return not_found_response("Governorate not found")
    
    # Check if governorate has users
    if governorate.users.count() > 0:
        return error_response("Cannot delete governorate with associated users", 400)
    
    try:
        db.session.delete(governorate)
        db.session.commit()
        return success_response(message="Governorate deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)
