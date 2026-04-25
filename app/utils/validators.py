"""
TORIDA Validators
=================
Input validation functions.
"""
import re
from typing import Dict, List, Tuple, Optional
from flask import request


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 150:
        return False, "Email must be less than 150 characters"
    
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format (Egyptian format).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    # Remove spaces and dashes
    phone = phone.replace(' ', '').replace('-', '')
    
    # Egyptian phone format: 20XXXXXXXXX or 0XXXXXXXXX
    phone_pattern = r'^(20)?[0-9]{10,11}$'
    
    if not re.match(phone_pattern, phone):
        return False, "Invalid phone number format"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for at least one uppercase, one lowercase, one digit
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None


def validate_required_fields(
    data: Dict, 
    required_fields: List[str]
) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Validate that all required fields are present and non-empty.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, errors_dict)
    """
    errors = {}
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors[field] = [f"{field.replace('_', ' ').title()} is required"]
    
    return len(errors) == 0, errors


def validate_pagination(page: int, per_page: int, max_per_page: int = 100) -> Tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number
        per_page: Items per page
        max_per_page: Maximum allowed items per page
        
    Returns:
        Tuple of (normalized_page, normalized_per_page)
    """
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    
    try:
        per_page = min(max(1, int(per_page)), max_per_page)
    except (TypeError, ValueError):
        per_page = 20
    
    return page, per_page


def validate_id(id_value: any, field_name: str = "ID") -> Tuple[bool, Optional[str]]:
    """
    Validate an ID value.
    
    Args:
        id_value: ID to validate
        field_name: Name of the field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        id_int = int(id_value)
        if id_int <= 0:
            return False, f"Invalid {field_name}"
        return True, None
    except (TypeError, ValueError):
        return False, f"Invalid {field_name}"


def validate_rating(rating: int) -> Tuple[bool, Optional[str]]:
    """
    Validate a rating value (1-5).
    
    Args:
        rating: Rating value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            return False, "Rating must be between 1 and 5"
        return True, None
    except (TypeError, ValueError):
        return False, "Invalid rating value"


def validate_price(price: any) -> Tuple[bool, Optional[str]]:
    """
    Validate a price value.
    
    Args:
        price: Price value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        price_float = float(price)
        if price_float < 0:
            return False, "Price cannot be negative"
        if price_float > 99999999.99:
            return False, "Price exceeds maximum value"
        return True, None
    except (TypeError, ValueError):
        return False, "Invalid price value"


def validate_quantity(quantity: any) -> Tuple[bool, Optional[str]]:
    """
    Validate a quantity value.
    
    Args:
        quantity: Quantity value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        quantity_int = int(quantity)
        if quantity_int < 0:
            return False, "Quantity cannot be negative"
        return True, None
    except (TypeError, ValueError):
        return False, "Invalid quantity value"


def sanitize_string(value: str, max_length: int = None) -> str:
    """
    Sanitize a string value.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Strip whitespace
    value = value.strip()
    
    # Truncate if needed
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value
