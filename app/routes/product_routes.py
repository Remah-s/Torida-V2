"""
Product Routes
==============
Routes for product management.
"""
from flask import Blueprint, request, current_app
import logging

from app.database import db
from app.models import Product, ProductImage, Category, ProductSequence, User
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response, validation_error_response
)
from app.utils.validators import (
    validate_required_fields, validate_pagination, 
    validate_price, validate_quantity
)
from app.utils.auth import token_required, seller_required
from app.utils.helpers import allowed_file, upload_file
from app.services.cloudinary_service import upload_image, delete_image

logger = logging.getLogger(__name__)

product_bp = Blueprint('products', __name__, url_prefix='/api/products')


@product_bp.route('', methods=['GET'])
def get_products():
    """Get all products with pagination and filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    # Filters
    category_id = request.args.get('category_id', type=int)
    company_id = request.args.get('company_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    is_active = request.args.get('is_active', type=str)
    search = request.args.get('search', type=str)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = Product.query
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if company_id:
        query = query.filter_by(company_id=company_id)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active_bool)
    else:
        # Default to active products only for public access
        query = query.filter_by(is_active=True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.product_name.ilike(search_filter),
                Product.description.ilike(search_filter)
            )
        )
    
    # Sorting
    sort_column = getattr(Product, sort_by, Product.created_at)
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    products = [product.to_dict_with_images() for product in pagination.items]
    
    return paginated_response(products, page, per_page, pagination.total)


@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID."""
    product = Product.query.get(product_id)
    
    if not product:
        return not_found_response("Product not found")
    
    return success_response(product.to_dict_with_reviews())


@product_bp.route('', methods=['POST'])
@token_required
def create_product():
    """Create a new product (Suppliers and Companies only)."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    # Check if user can sell
    user = User.query.get(g.current_user_id)
    if not user or not user.can_sell():
        return error_response("Only suppliers and companies can create products", 403)
    
    required_fields = ['category_id', 'product_name', 'price']
    is_valid, errors = validate_required_fields(data, required_fields)
    
    if not is_valid:
        return validation_error_response(errors)
    
    # Validate price
    is_valid, error_msg = validate_price(data['price'])
    if not is_valid:
        return error_response(error_msg, 400)
    
    # Validate category
    category = Category.query.get(data['category_id'])
    if not category:
        return error_response("Invalid category", 400)
    
    # Validate stock quantity if provided
    if 'stock_quantity' in data:
        is_valid, error_msg = validate_quantity(data['stock_quantity'])
        if not is_valid:
            return error_response(error_msg, 400)
    
    try:
        # Generate product code
        category_id = data['category_id']
        
        # Get or create product sequence
        prod_seq = ProductSequence.query.filter_by(category_id=category_id).first()
        if not prod_seq:
            prod_seq = ProductSequence(category_id=category_id, sequence=0)
            db.session.add(prod_seq)
            db.session.flush()
        
        prod_seq.sequence += 1
        sequence = prod_seq.sequence
        
        # Generate code and custom_id
        code = f"{str(category_id).zfill(3)}{str(sequence).zfill(3)}"
        custom_id = f"PRD-{code}"
        
        # Create product
        product = Product(
            code=code,
            custom_id=custom_id,
            company_id=g.current_user_id,
            category_id=category_id,
            product_name=data['product_name'],
            description=data.get('description'),
            price=data['price'],
            stock_quantity=data.get('stock_quantity', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(product)
        db.session.flush()  # Flush to get the product ID
        
        # Add image if image_url provided
        if 'image_url' in data and data['image_url']:
            image = ProductImage(
                product_id=product.id,
                image_url=data['image_url'],
                is_primary=True
            )
            db.session.add(image)
            logger.info(f"Primary image added to product {product.id}: {data['image_url']}")
        
        db.session.commit()
        
        logger.info(f"Product created: {product.custom_id}")
        return created_response(product.to_dict(), "Product created successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Product creation failed: {str(e)}", exc_info=True)
        return error_response(f"Product creation failed: {str(e)}", 500)


@product_bp.route('/upload-image', methods=['POST'])
@token_required
def upload_product_image():
    """
    Upload image to Cloudinary.
    
    Returns:
        {
            "success": true,
            "image_url": "https://res.cloudinary.com/..."
        }
    """
    from flask import g
    
    # Check if user can sell
    user = User.query.get(g.current_user_id)
    if not user or not user.can_sell():
        return error_response("Only suppliers and companies can upload images", 403)
    
    # Check for image file
    if 'image' not in request.files:
        return error_response("No image file provided", 400)
    
    file = request.files['image']
    
    if file.filename == '':
        return error_response("No image file selected", 400)
    
    # Get configuration
    max_size = current_app.config.get('MAX_IMAGE_SIZE', 10485760)  # 10MB
    allowed_extensions = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'jpg', 'jpeg', 'png', 'webp'})
    
    try:
        # Upload to Cloudinary
        success, image_url, error_msg = upload_image(
            file,
            folder='torida/products',
            max_size=max_size,
            allowed_extensions=allowed_extensions
        )
        
        if not success:
            logger.warning(f"Image upload failed for user {g.current_user_id}: {error_msg}")
            return error_response(error_msg, 400)
        
        logger.info(f"Image uploaded successfully for user {g.current_user_id}: {image_url}")
        
        return success_response({
            'image_url': image_url
        }, "Image uploaded successfully")
        
    except Exception as e:
        logger.error(f"Unexpected error uploading image: {str(e)}", exc_info=True)
        return error_response(f"Image upload failed: {str(e)}", 500)


@product_bp.route('/<int:product_id>', methods=['PUT'])
@token_required
def update_product(product_id):
    """Update product."""
    from flask import g
    data = request.get_json()
    
    if not data:
        return error_response("No data provided", 400)
    
    product = Product.query.get(product_id)
    
    if not product:
        return not_found_response("Product not found")
    
    # Authorization check
    if product.company_id != g.current_user_id:
        return error_response("Not authorized to update this product", 403)
    
    if 'product_name' in data:
        product.product_name = data['product_name']
    
    if 'description' in data:
        product.description = data['description']
    
    if 'price' in data:
        is_valid, error_msg = validate_price(data['price'])
        if not is_valid:
            return error_response(error_msg, 400)
        product.price = data['price']
    
    if 'stock_quantity' in data:
        is_valid, error_msg = validate_quantity(data['stock_quantity'])
        if not is_valid:
            return error_response(error_msg, 400)
        product.stock_quantity = data['stock_quantity']
    
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])
    
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return error_response("Invalid category", 400)
        product.category_id = data['category_id']
    
    try:
        db.session.commit()
        return success_response(product.to_dict(), "Product updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(product_id):
    """Delete product."""
    from flask import g
    product = Product.query.get(product_id)
    
    if not product:
        return not_found_response("Product not found")
    
    # Authorization check
    if product.company_id != g.current_user_id:
        return error_response("Not authorized to delete this product", 403)
    
    try:
        db.session.delete(product)
        db.session.commit()
        return success_response(message="Product deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Delete failed: {str(e)}", 500)


@product_bp.route('/<int:product_id>/images', methods=['GET'])
def get_product_images(product_id):
    """Get product images."""
    product = Product.query.get(product_id)
    
    if not product:
        return not_found_response("Product not found")
    
    images = [img.to_dict() for img in product.images]
    
    return success_response(images)


@product_bp.route('/<int:product_id>/images', methods=['POST'])
@token_required
def add_product_image(product_id):
    """Add image to product using Cloudinary."""
    from flask import g
    product = Product.query.get(product_id)
    
    if not product:
        return not_found_response("Product not found")
    
    # Authorization check
    if product.company_id != g.current_user_id:
        return error_response("Not authorized to add images to this product", 403)
    
    # Check for image in request
    if 'image' not in request.files:
        return error_response("No image file provided", 400)
    
    file = request.files['image']
    
    if file.filename == '':
        return error_response("No image file selected", 400)
    
    # Get configuration
    max_size = current_app.config.get('MAX_IMAGE_SIZE', 10485760)  # 10MB
    allowed_extensions = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'jpg', 'jpeg', 'png', 'webp'})
    
    try:
        # Upload to Cloudinary
        success, image_url, error_msg = upload_image(
            file,
            folder='torida/products',
            max_size=max_size,
            allowed_extensions=allowed_extensions
        )
        
        if not success:
            logger.warning(f"Image upload failed: {error_msg}")
            return error_response(error_msg, 400)
        
        # Create image record
        is_primary = request.form.get('is_primary', 'false').lower() == 'true'
        
        # If setting as primary, unset other primary images
        if is_primary:
            ProductImage.query.filter_by(
                product_id=product_id, 
                is_primary=True
            ).update({'is_primary': False})
        
        image = ProductImage(
            product_id=product_id,
            image_url=image_url,
            is_primary=is_primary
        )
        
        db.session.add(image)
        db.session.commit()
        
        logger.info(f"Product image added: product_id={product_id}, image_url={image_url}")
        
        return created_response(image.to_dict(), "Image added successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Image addition failed: {str(e)}", exc_info=True)
        return error_response(f"Image upload failed: {str(e)}", 500)


@product_bp.route('/<int:product_id>/images/<int:image_id>', methods=['DELETE'])
@token_required
def delete_product_image(product_id, image_id):
    """Delete product image from Cloudinary and database."""
    from flask import g
    product = Product.query.get(product_id)
    
    if not product:
        return not_found_response("Product not found")
    
    # Authorization check
    if product.company_id != g.current_user_id:
        return error_response("Not authorized to delete images from this product", 403)
    
    image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
    
    if not image:
        return not_found_response("Image not found")
    
    try:
        # Delete from Cloudinary
        image_url = image.image_url
        success, error_msg = delete_image(image_url)
        
        if not success:
            logger.warning(f"Failed to delete image from Cloudinary: {error_msg}")
            # Continue with database deletion even if Cloudinary deletion fails
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        logger.info(f"Product image deleted: product_id={product_id}, image_id={image_id}")
        return success_response(message="Image deleted successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Image deletion failed: {str(e)}", exc_info=True)
        return error_response(f"Delete failed: {str(e)}", 500)


@product_bp.route('/<int:product_id>/images/<int:image_id>/set-primary', methods=['POST'])
@token_required
def set_primary_image(product_id, image_id):
    """Set image as primary."""
    from flask import g
    product = Product.query.get(product_id)
    
    if not product:
        return not_found_response("Product not found")
    
    # Authorization check
    if product.company_id != g.current_user_id:
        return error_response("Not authorized", 403)
    
    image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
    
    if not image:
        return not_found_response("Image not found")
    
    try:
        # Unset other primary images
        ProductImage.query.filter_by(
            product_id=product_id, 
            is_primary=True
        ).update({'is_primary': False})
        
        image.is_primary = True
        db.session.commit()
        
        return success_response(message="Primary image set successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed: {str(e)}", 500)


@product_bp.route('/my-products', methods=['GET'])
@token_required
def get_my_products():
    """Get products created by current user."""
    from flask import g
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    page, per_page = validate_pagination(page, per_page)
    
    query = Product.query.filter_by(company_id=g.current_user_id)
    query = query.order_by(Product.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    products = [product.to_dict_with_images() for product in pagination.items]
    
    return paginated_response(products, page, per_page, pagination.total)
