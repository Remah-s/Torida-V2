"""
Notification Routes
===================
Routes for notification management.
"""
from flask import Blueprint, request

from app.database import db
from app.models import Notification
from app.utils.response import (
    success_response, error_response,
    not_found_response, paginated_response
)
from app.utils.validators import validate_pagination
from app.utils.auth import token_required
from app.services.notification_service import NotificationService

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


@notification_bp.route('', methods=['GET'])
@token_required
def get_notifications():
    """Get current user's notifications."""
    from flask import g
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    user_id = g.current_user_id
    
    # Filter by read status
    is_read = request.args.get('is_read')
    
    query = Notification.query.filter_by(user_id=user_id)
    
    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        query = query.filter_by(is_read=is_read_bool)
    
    query = query.order_by(Notification.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    notifications = [n.to_dict() for n in pagination.items]
    
    return paginated_response(notifications, page, per_page, pagination.total)


@notification_bp.route('/unread-count', methods=['GET'])
@token_required
def get_unread_count():
    """Get count of unread notifications."""
    from flask import g
    user_id = g.current_user_id
    
    count = NotificationService.get_unread_count(user_id)
    
    return success_response({'unread_count': count})


@notification_bp.route('/<int:notification_id>', methods=['GET'])
@token_required
def get_notification(notification_id):
    """Get notification by ID."""
    from flask import g
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return not_found_response("Notification not found")
    
    # Authorization check
    if notification.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    return success_response(notification.to_dict())


@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@token_required
def mark_as_read(notification_id):
    """Mark notification as read."""
    from flask import g
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return not_found_response("Notification not found")
    
    # Authorization check
    if notification.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    try:
        notification.mark_read()
        db.session.commit()
        return success_response(message="Notification marked as read")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed: {str(e)}", 500)


@notification_bp.route('/read-all', methods=['POST'])
@token_required
def mark_all_as_read():
    """Mark all notifications as read."""
    from flask import g
    user_id = g.current_user_id
    
    NotificationService.mark_all_read(user_id)
    
    return success_response(message="All notifications marked as read")


@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
@token_required
def delete_notification(notification_id):
    """Delete notification."""
    from flask import g
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return not_found_response("Notification not found")
    
    # Authorization check
    if notification.user_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    try:
        db.session.delete(notification)
        db.session.commit()
        return success_response(message="Notification deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)
