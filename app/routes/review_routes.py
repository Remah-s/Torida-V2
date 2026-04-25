"""
Review Routes
=============
Routes for product review management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import ProductReview, Product, User
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import validate_required_fields, validate_pagination, validate_rating
from app.utils.auth import token_required
from app.services.notification_service import NotificationService

review_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')


@review_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """Get reviews for a product."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    product = Product.query.get(product_id)
    if not product:
        return not_found_response("Product not found")
    
    query = ProductReview.query.filter_by(product_id=product_id)
    query = query.order_by(ProductReview.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    reviews = [review.to_dict() for review in pagination.items]
    
    return paginated_response(reviews, page, per_page, pagination.total)


@review_bp.route('', methods=['POST'])
@token_required
def create_review():
    """Create a product review."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    required_fields = ['product_id', 'rating']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Validate rating
    is_valid, error_msg = validate_rating(data['rating'])
    if not is_valid:
        return error_response(error_msg, 400)
    
    # Check product exists
    product = Product.query.get(data['product_id'])
    if not product:
        return not_found_response("Product not found")
    
    user_id = g.current_user_id
    
    # Check if already reviewed
    existing = ProductReview.query.filter_by(
        product_id=data['product_id'],
        user_id=user_id
    ).first()
    
    if existing:
        return error_response("You have already reviewed this product", 400)
    
    try:
        review = ProductReview(
            product_id=data['product_id'],
            user_id=user_id,
            rating=data['rating'],
            comment=data.get('comment')
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Notify seller
        user = User.query.get(user_id)
        NotificationService.notify_new_review(product, user.full_name)
        
        return created_response(review.to_dict(), "Review submitted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Review creation failed: {str(e)}", 500)


@review_bp.route('/<int:review_id>', methods=['PUT'])
@token_required
def update_review(review_id):
    """Update a review."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    review = ProductReview.query.get(review_id)
    
    if not review:
        return not_found_response("Review not found")
    
    # Authorization check
    if review.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    if 'rating' in data:
        is_valid, error_msg = validate_rating(data['rating'])
        if not is_valid:
            return error_response(error_msg, 400)
        review.rating = data['rating']
    
    if 'comment' in data:
        review.comment = data['comment']
    
    try:
        db.session.commit()
        return success_response(review.to_dict(), "Review updated")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@review_bp.route('/<int:review_id>', methods=['DELETE'])
@token_required
def delete_review(review_id):
    """Delete a review."""
    from flask import g
    review = ProductReview.query.get(review_id)
    
    if not review:
        return not_found_response("Review not found")
    
    # Authorization check
    if review.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    try:
        db.session.delete(review)
        db.session.commit()
        return success_response(message="Review deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)


@review_bp.route('/my-reviews', methods=['GET'])
@token_required
def get_my_reviews():
    """Get current user's reviews."""
    from flask import g
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    user_id = g.current_user_id
    
    query = ProductReview.query.filter_by(user_id=user_id)
    query = query.order_by(ProductReview.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    reviews = [review.to_dict() for review in pagination.items]
    
    return paginated_response(reviews, page, per_page, pagination.total)
