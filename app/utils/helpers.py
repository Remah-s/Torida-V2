"""
TORIDA Helper Functions
=======================
General utility helper functions.
"""
import os
import random
import string
import secrets
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app, has_request_context, request
from typing import Optional, Tuple


def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP code.
    
    Args:
        length: Length of the OTP (default 6)
        
    Returns:
        OTP string
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def generate_random_string(length: int = 32) -> str:
    """
    Generate a random string.
    
    Args:
        length: Length of the string
        
    Returns:
        Random string
    """
    return secrets.token_hex(length // 2)


def generate_uuid() -> str:
    """
    Generate a UUID string.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def allowed_file(filename: str, allowed_extensions: list = None) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (without dots)
        
    Returns:
        True if file extension is allowed
    """
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 
                                                     ['png', 'jpg', 'jpeg', 'gif', 'webp'])
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (lowercase, without dot)
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def upload_file(file, subfolder: str = '') -> Tuple[bool, Optional[str]]:
    """
    Upload a file to the upload folder.
    
    Args:
        file: FileStorage object
        subfolder: Subfolder within uploads
        
    Returns:
        Tuple of (success, filepath_or_error)
    """
    try:
        if not file:
            return False, "No file provided"
        
        if not allowed_file(file.filename):
            return False, "File type not allowed"
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if subfolder:
            upload_folder = os.path.join(upload_folder, subfolder)
        
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        extension = get_file_extension(original_filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{generate_random_string(8)}.{extension}"
        
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        
        # Return relative path
        relative_path = os.path.join(subfolder, unique_filename) if subfolder else unique_filename
        return True, relative_path
    
    except Exception as e:
        return False, str(e)


def build_public_url(path: str) -> str:
    """
    Build a public absolute URL for a stored asset path when possible.

    Args:
        path: Relative or absolute asset path

    Returns:
        Absolute URL when a public base is available, otherwise the original path
    """
    if not path:
        return path

    if path.startswith(('http://', 'https://')):
        return path

    normalized_path = path if path.startswith('/') else f'/{path}'

    base_url = current_app.config.get('PUBLIC_API_BASE_URL', '').rstrip('/')
    if not base_url and has_request_context():
        base_url = request.host_url.rstrip('/')

    if not base_url:
        return normalized_path

    return f'{base_url}{normalized_path}'


def sanitize_input(value: str) -> str:
    """
    Sanitize user input.
    
    Args:
        value: Input string
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    return value


def format_phone(phone: str) -> str:
    """
    Format phone number to standard format.
    
    Args:
        phone: Phone number string
        
    Returns:
        Formatted phone number
    """
    if not phone:
        return ""
    
    # Remove spaces, dashes, and parentheses
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Add Egypt country code if missing
    if phone.startswith('0'):
        phone = '2' + phone
    
    return phone


def calculate_pagination(page: int, per_page: int, total: int) -> dict:
    """
    Calculate pagination details.
    
    Args:
        page: Current page
        per_page: Items per page
        total: Total items
        
    Returns:
        Pagination dict
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    
    return {
        'page': page,
        'per_page': per_page,
        'total_items': total,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'next_page': page + 1 if page < total_pages else None,
        'prev_page': page - 1 if page > 1 else None
    }


def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format a datetime object to string.
    
    Args:
        dt: Datetime object
        format_str: Output format string
        
    Returns:
        Formatted datetime string
    """
    if not dt:
        return ""
    return dt.strftime(format_str)


def parse_datetime(dt_string: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """
    Parse a datetime string to datetime object.
    
    Args:
        dt_string: Datetime string
        format_str: Input format string
        
    Returns:
        Datetime object or None
    """
    if not dt_string:
        return None
    
    try:
        return datetime.strptime(dt_string, format_str)
    except ValueError:
        return None


def generate_order_number(order_id: int) -> str:
    """
    Generate a human-readable order number.
    
    Args:
        order_id: Order ID
        
    Returns:
        Order number string (e.g., ORD-000001)
    """
    return f"ORD-{str(order_id).zfill(6)}"


def mask_email(email: str) -> str:
    """
    Mask an email address for privacy.
    
    Args:
        email: Email address
        
    Returns:
        Masked email (e.g., a***@example.com)
    """
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 2:
        masked = local[0] + '*'
    else:
        masked = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask a phone number for privacy.
    
    Args:
        phone: Phone number
        
    Returns:
        Masked phone (e.g., 201***1234)
    """
    if not phone or len(phone) < 6:
        return phone
    
    return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]
