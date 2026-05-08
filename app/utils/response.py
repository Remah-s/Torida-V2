"""
TORIDA Response Helpers
=======================
Standardized API response functions.
"""
from flask import jsonify
from typing import Any, Optional, Dict, List


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> tuple:
    """
    Create a standardized success response.
    
    Args:
        data: Response data (dict, list, or any serializable object)
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return jsonify(response), status_code


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    errors: Optional[Dict[str, List[str]]] = None,
    code: Optional[str] = None
) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        errors: Optional validation errors dict
        code: Optional machine-readable error code (e.g. "ROLE_NOT_FOUND")
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        "success": False,
        "error": message,
        "message": message
    }
    
    if code:
        response["code"] = code
    
    if errors:
        response["errors"] = errors
    
    return jsonify(response), status_code


def paginated_response(
    items: list,
    page: int,
    per_page: int,
    total: int,
    message: str = "Success"
) -> tuple:
    """
    Create a standardized paginated response.
    
    Args:
        items: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        message: Success message
        
    Returns:
        Tuple of (response, status_code)
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    
    response = {
        "success": True,
        "message": message,
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    }
    
    return jsonify(response), 200


def created_response(
    data: Any = None,
    message: str = "Resource created successfully"
) -> tuple:
    """Create a 201 Created response."""
    return success_response(data, message, 201)


def no_content_response() -> tuple:
    """Create a 204 No Content response."""
    return '', 204


def not_found_response(message: str = "Resource not found") -> tuple:
    """Create a 404 Not Found response."""
    return error_response(message, 404)


def unauthorized_response(message: str = "Unauthorized access") -> tuple:
    """Create a 401 Unauthorized response."""
    return error_response(message, 401)


def forbidden_response(message: str = "Access forbidden") -> tuple:
    """Create a 403 Forbidden response."""
    return error_response(message, 403)


def validation_error_response(errors: Dict[str, List[str]]) -> tuple:
    """Create a 422 Validation Error response."""
    return error_response("Validation failed", 422, errors)
