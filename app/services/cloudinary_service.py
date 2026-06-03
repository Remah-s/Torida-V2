"""
Cloudinary Service
==================
Service for uploading images to Cloudinary and managing image URLs.
"""
import logging
import os
from typing import Tuple, Optional
from werkzeug.datastructures import FileStorage
import cloudinary.uploader

logger = logging.getLogger(__name__)


def validate_image_file(file: FileStorage, max_size: int, allowed_extensions: set) -> Tuple[bool, Optional[str]]:
    """
    Validate image file before upload.
    
    Args:
        file: FileStorage object from request
        max_size: Maximum file size in bytes
        allowed_extensions: Set of allowed file extensions (lowercase)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if not file.filename:
        return False, "File must have a name"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f"File size exceeds maximum of {max_size_mb:.1f}MB"
    
    if file_size == 0:
        return False, "File is empty"
    
    # Check file extension
    filename = file.filename.lower()
    if '.' not in filename:
        return False, "File must have an extension"
    
    file_ext = filename.rsplit('.', 1)[-1]
    
    if file_ext not in allowed_extensions:
        allowed = ', '.join(sorted(allowed_extensions))
        return False, f"File type not allowed. Allowed types: {allowed}"
    
    return True, None


def upload_image(
    file: FileStorage,
    folder: str = 'torida/products',
    max_size: int = 10485760,  # 10MB default
    allowed_extensions: Optional[set] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Upload image to Cloudinary.
    
    Args:
        file: FileStorage object from request
        folder: Cloudinary folder path
        max_size: Maximum file size in bytes
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        Tuple of (success, image_url, error_message)
        - If successful: (True, image_url, None)
        - If failed: (False, None, error_message)
    """
    if allowed_extensions is None:
        allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
    
    # Validate file
    is_valid, error_msg = validate_image_file(file, max_size, allowed_extensions)
    if not is_valid:
        logger.warning(f"Image validation failed: {error_msg}")
        return False, None, error_msg
    
    try:
        # Upload to Cloudinary
        logger.info(f"Uploading image to Cloudinary folder: {folder}")
        
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type='auto',
            quality='auto',
            fetch_format='auto',
            use_filename=True,
            unique_filename=True
        )
        
        # Extract secure URL
        image_url = result.get('secure_url')
        
        if not image_url:
            error_msg = "Upload succeeded but no URL returned"
            logger.error(f"Cloudinary upload failed: {error_msg}")
            return False, None, error_msg
        
        logger.info(f"Image uploaded successfully: {image_url}")
        return True, image_url, None
        
    except Exception as e:
        error_msg = f"Cloudinary upload error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, None, error_msg


def delete_image(image_url: str) -> Tuple[bool, Optional[str]]:
    """
    Delete image from Cloudinary.
    
    Args:
        image_url: Cloudinary image URL or public_id
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        if not image_url:
            return False, "No image URL provided"
        
        # Try to extract public_id from URL if full URL is provided
        if image_url.startswith('http'):
            # Extract public_id from URL like:
            # https://res.cloudinary.com/dswqa76wb/image/upload/v1234567890/torida/products/filename.jpg
            parts = image_url.split('/upload/')
            if len(parts) > 1:
                public_id = '/'.join(parts[1].split('/')[1:]).rsplit('.', 1)[0]
            else:
                public_id = image_url
        else:
            public_id = image_url
        
        logger.info(f"Deleting image from Cloudinary: {public_id}")
        
        result = cloudinary.uploader.destroy(public_id)
        
        if result.get('result') == 'ok':
            logger.info(f"Image deleted successfully: {public_id}")
            return True, None
        else:
            error_msg = f"Failed to delete image: {result}"
            logger.error(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"Cloudinary delete error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
