"""
Business Profile Routes
=======================
Routes for business profile management.
"""
import logging

from flask import Blueprint, request, current_app, g

from app.database import db
from app.models import BusinessProfile, User
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination
from app.utils.auth import token_required
from app.services.cloudinary_service import upload_image

business_profile_bp = Blueprint('business_profiles', __name__, url_prefix='/api/business-profiles')
logger = logging.getLogger(__name__)


PROFILE_PHOTO_FIELDS = {
    'logo': 'logo_url',
    'business_logo': 'logo_url',
    'profile': 'logo_url',
    'cover': 'cover_image_url',
    'cover_image': 'cover_image_url',
}


@business_profile_bp.route('', methods=['GET'])
@token_required
def get_business_profiles():
    """Get all business profiles with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    query = BusinessProfile.query.order_by(BusinessProfile.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    profiles = [profile.to_dict() for profile in pagination.items]
    
    return paginated_response(profiles, page, per_page, pagination.total)


@business_profile_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_business_profile(user_id):
    """Get business profile by user ID."""
    profile = BusinessProfile.query.get(user_id)
    
    if not profile:
        return not_found_response("Business profile not found")
    
    return success_response(profile.to_dict())


@business_profile_bp.route('', methods=['POST'])
@token_required
def create_business_profile():
    """Create a business profile."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['business_name', 'address']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Get user_id from data or current user
    user_id = data.get('user_id', g.current_user_id)
    
    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return not_found_response("User not found")
    
    # Check if user already has a business profile
    if BusinessProfile.query.get(user_id):
        return error_response("User already has a business profile", 400)
    
    # Check for unique constraints
    if data.get('tax_number'):
        if BusinessProfile.query.filter_by(tax_number=data['tax_number']).first():
            return error_response("Tax number already registered", 400)
    
    if data.get('commercial_register'):
        if BusinessProfile.query.filter_by(commercial_register=data['commercial_register']).first():
            return error_response("Commercial register already registered", 400)
    
    try:
        profile = BusinessProfile(
            user_id=user_id,
            business_name=data['business_name'],
            tax_number=data.get('tax_number'),
            commercial_register=data.get('commercial_register'),
            address=data['address'],
            logo_url=data.get('logo_url'),
            cover_image_url=data.get('cover_image_url')
        )
        db.session.add(profile)
        db.session.commit()
        
        return created_response(profile.to_dict(), "Business profile created successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Business profile creation failed: {str(e)}", 500)


@business_profile_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_business_profile(user_id):
    """Update business profile."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    profile = BusinessProfile.query.get(user_id)
    
    if not profile:
        return not_found_response("Business profile not found")
    
    # Authorization check
    if g.current_user_id != user_id:
        return error_response("Not authorized to update this profile", 403)
    
    if 'business_name' in data:
        profile.business_name = data['business_name']
    
    if 'address' in data:
        profile.address = data['address']
    
    if 'tax_number' in data:
        # Check if tax number is taken
        existing = BusinessProfile.query.filter(
            BusinessProfile.tax_number == data['tax_number'],
            BusinessProfile.user_id != user_id
        ).first()
        if existing:
            return error_response("Tax number already in use", 400)
        profile.tax_number = data['tax_number']
    
    if 'commercial_register' in data:
        # Check if commercial register is taken
        existing = BusinessProfile.query.filter(
            BusinessProfile.commercial_register == data['commercial_register'],
            BusinessProfile.user_id != user_id
        ).first()
        if existing:
            return error_response("Commercial register already in use", 400)
        profile.commercial_register = data['commercial_register']

    if 'logo_url' in data:
        profile.logo_url = data['logo_url']

    if 'cover_image_url' in data:
        profile.cover_image_url = data['cover_image_url']
    
    try:
        db.session.commit()
        return success_response(profile.to_dict(), "Business profile updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@business_profile_bp.route('/me/upload-photo', methods=['POST'])
@token_required
def upload_my_business_profile_photo():
    """
    Upload a supplier/company profile photo from local multipart form data.

    Form fields:
      image: local image file
      photo_type: logo, cover, profile, business_logo, or cover_image
    """
    user = User.query.get(g.current_user_id)
    if not user or not user.can_sell():
        return error_response("Only suppliers and companies can upload profile photos", 403)

    profile = BusinessProfile.query.get(g.current_user_id)
    if not profile:
        return not_found_response("Business profile not found. Create profile before uploading photos")

    if 'image' not in request.files:
        return error_response("No image file provided", 400)

    file = request.files['image']
    if file.filename == '':
        return error_response("No image file selected", 400)

    photo_type = request.form.get('photo_type', 'logo').strip().lower()
    profile_field = PROFILE_PHOTO_FIELDS.get(photo_type)
    if not profile_field:
        return error_response("photo_type must be one of: logo, cover, profile, business_logo, cover_image", 400)

    max_size = current_app.config.get('MAX_IMAGE_SIZE', 10485760)
    allowed_extensions = current_app.config.get(
        'ALLOWED_IMAGE_EXTENSIONS',
        {'jpg', 'jpeg', 'png', 'webp'}
    )

    try:
        success, image_url, error_msg = upload_image(
            file,
            folder=f'torida/business-profiles/{g.current_user_id}',
            max_size=max_size,
            allowed_extensions=allowed_extensions
        )

        if not success:
            logger.warning(
                "Business profile photo upload failed for user %s: %s",
                g.current_user_id,
                error_msg
            )
            return error_response(error_msg, 400)

        setattr(profile, profile_field, image_url)
        db.session.commit()

        return success_response({
            'image_url': image_url,
            'photo_type': photo_type,
            'profile_field': profile_field,
            'profile': profile.to_dict()
        }, "Profile photo uploaded successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(
            "Unexpected error uploading business profile photo: %s",
            str(e),
            exc_info=True
        )
        return error_response(f"Profile photo upload failed: {str(e)}", 500)


@business_profile_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
def delete_business_profile(user_id):
    """Delete business profile."""
    from flask import g
    profile = BusinessProfile.query.get(user_id)
    
    if not profile:
        return not_found_response("Business profile not found")
    
    # Authorization check
    if g.current_user_id != user_id:
        return error_response("Not authorized to delete this profile", 403)
    
    try:
        db.session.delete(profile)
        db.session.commit()
        return success_response(message="Business profile deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)
