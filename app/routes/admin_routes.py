"""
Admin Routes
============
Routes for admin control panel - full access to all entities.
"""
from flask import Blueprint, request, g
from datetime import datetime, timedelta
from sqlalchemy import func, desc

from app.database import db
from app.models import (
    User, UserType, Governorate, UserRole, Role, Permission, RolePermission,
    Product, ProductImage, ProductReview, Category,
    Order, OrderItem, OrderStatusHistory, Payment,
    Cart, CartItem, Wishlist, Notification, BusinessProfile
)
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, paginated_response
)
from app.utils.validators import validate_pagination
from app.utils.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ============================================
# DASHBOARD & ANALYTICS
# ============================================

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """Get admin dashboard stats."""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_categories = Category.query.count()

    # Revenue
    total_revenue = db.session.query(func.sum(Order.total_price)).filter(
        Order.status.notin_(['cancelled', 'refunded'])
    ).scalar() or 0

    # Monthly revenue
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_revenue = db.session.query(func.sum(Order.total_price)).filter(
        Order.created_at >= thirty_days_ago,
        Order.status.notin_(['cancelled', 'refunded'])
    ).scalar() or 0

    # Recent orders
    recent_orders = Order.query.order_by(desc(Order.created_at)).limit(10).all()

    # Recent users
    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()

    # User type breakdown
    user_types = db.session.query(
        UserType.type_name, func.count(User.id)
    ).join(User, User.type_id == UserType.id).group_by(UserType.type_name).all()

    # Order status breakdown
    order_statuses = db.session.query(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()

    return success_response({
        'total_users': total_users,
        'active_users': active_users,
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_categories': total_categories,
        'total_revenue': float(total_revenue),
        'monthly_revenue': float(monthly_revenue),
        'recent_orders': [o.to_dict() for o in recent_orders],
        'recent_users': [u.to_dict() for u in recent_users],
        'user_type_breakdown': [{'type': t, 'count': c} for t, c in user_types],
        'order_status_breakdown': [{'status': s, 'count': c} for s, c in order_statuses],
    })


@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get analytics data for charts."""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    # Daily orders
    daily_orders = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('count'),
        func.sum(Order.total_price).label('revenue')
    ).filter(Order.created_at >= start_date).group_by(
        func.date(Order.created_at)
    ).order_by(func.date(Order.created_at)).all()

    # Daily new users
    daily_users = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= start_date).group_by(
        func.date(User.created_at)
    ).order_by(func.date(User.created_at)).all()

    # Top products by order count
    top_products = db.session.query(
        Product.product_name,
        func.count(OrderItem.id).label('order_count'),
        func.sum(OrderItem.quantity).label('total_qty')
    ).join(OrderItem, OrderItem.product_id == Product.id).group_by(
        Product.id, Product.product_name
    ).order_by(desc('order_count')).limit(10).all()

    # Top sellers by revenue
    top_sellers = db.session.query(
        User.full_name,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_price).label('total_revenue')
    ).join(Order, Order.seller_id == User.id).filter(
        Order.status.notin_(['cancelled', 'refunded'])
    ).group_by(User.id, User.full_name).order_by(
        desc('total_revenue')
    ).limit(10).all()

    return success_response({
        'daily_orders': [{'date': str(d.date), 'count': d.count, 'revenue': float(d.revenue or 0)} for d in daily_orders],
        'daily_users': [{'date': str(d.date), 'count': d.count} for d in daily_users],
        'top_products': [{'name': p.product_name, 'orders': p.order_count, 'qty': int(p.total_qty or 0)} for p in top_products],
        'top_sellers': [{'name': s.full_name, 'orders': s.order_count, 'revenue': float(s.total_revenue or 0)} for s in top_sellers],
    })


# ============================================
# USER MANAGEMENT
# ============================================

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with filters."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    page, per_page = validate_pagination(page, per_page)

    type_id = request.args.get('type_id', type=int)
    gov_id = request.args.get('gov_id', type=int)
    is_active = request.args.get('is_active', type=str)
    search = request.args.get('search', type=str)

    query = User.query
    if type_id:
        query = query.filter_by(type_id=type_id)
    if gov_id:
        query = query.filter_by(gov_id=gov_id)
    if is_active is not None and is_active != '':
        query = query.filter_by(is_active=is_active.lower() == 'true')
    if search:
        sf = f"%{search}%"
        query = query.filter(db.or_(
            User.full_name.ilike(sf), User.email.ilike(sf), User.phone.ilike(sf)
        ))

    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = [u.to_dict(include_sensitive=True) for u in pagination.items]
    return paginated_response(users, page, per_page, pagination.total)


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get full user detail."""
    user = User.query.get(user_id)
    if not user:
        return not_found_response("User not found")

    data = user.to_dict(include_sensitive=True)
    data['orders_count'] = user.buyer_orders.count() + user.seller_orders.count()
    data['products_count'] = user.products.count()
    data['reviews_count'] = user.reviews.count()
    return success_response(data)


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update any user field."""
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400)

    user = User.query.get(user_id)
    if not user:
        return not_found_response("User not found")

    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
        if existing:
            return error_response("Email already in use", 400)
        user.email = data['email']
    if 'phone' in data:
        existing = User.query.filter(User.phone == data['phone'], User.id != user_id).first()
        if existing:
            return error_response("Phone already in use", 400)
        user.phone = data['phone']
    if 'gov_id' in data:
        user.gov_id = data['gov_id']
    if 'type_id' in data:
        user.type_id = data['type_id']
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])

    try:
        db.session.commit()
        return success_response(user.to_dict(include_sensitive=True), "User updated")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Update failed: {str(e)}", 500)


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Soft delete (deactivate) user."""
    user = User.query.get(user_id)
    if not user:
        return not_found_response("User not found")
    user.is_active = False
    try:
        db.session.commit()
        return success_response(message="User deactivated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status."""
    user = User.query.get(user_id)
    if not user:
        return not_found_response("User not found")
    user.is_active = not user.is_active
    try:
        db.session.commit()
        return success_response(user.to_dict(), f"User {'activated' if user.is_active else 'deactivated'}")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@admin_required
def admin_assign_role(user_id):
    """Assign role to user."""
    data = request.get_json()
    if not data or not data.get('role_id'):
        return error_response("Role ID required", 400)

    user = User.query.get(user_id)
    if not user:
        return not_found_response("User not found")

    role = Role.query.get(data['role_id'])
    if not role:
        return not_found_response("Role not found")

    existing = UserRole.query.filter_by(user_id=user_id, role_id=data['role_id']).first()
    if existing:
        return error_response("Role already assigned", 400)

    try:
        ur = UserRole(user_id=user_id, role_id=data['role_id'])
        db.session.add(ur)
        db.session.commit()
        return success_response(message="Role assigned")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@admin_required
def admin_remove_role(user_id, role_id):
    """Remove role from user."""
    ur = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if not ur:
        return not_found_response("Role assignment not found")
    try:
        db.session.delete(ur)
        db.session.commit()
        return success_response(message="Role removed")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================
# PRODUCT MANAGEMENT
# ============================================

@admin_bp.route('/products', methods=['GET'])
@admin_required
def get_products():
    """Get all products with filters."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    page, per_page = validate_pagination(page, per_page)

    category_id = request.args.get('category_id', type=int)
    company_id = request.args.get('company_id', type=int)
    is_active = request.args.get('is_active', type=str)
    search = request.args.get('search', type=str)

    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if company_id:
        query = query.filter_by(company_id=company_id)
    if is_active is not None and is_active != '':
        query = query.filter_by(is_active=is_active.lower() == 'true')
    if search:
        sf = f"%{search}%"
        query = query.filter(db.or_(
            Product.product_name.ilike(sf), Product.description.ilike(sf)
        ))

    query = query.order_by(Product.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = [p.to_dict_with_images() for p in pagination.items]
    return paginated_response(products, page, per_page, pagination.total)


@admin_bp.route('/products/<int:product_id>', methods=['GET'])
@admin_required
def get_product(product_id):
    """Get full product detail."""
    product = Product.query.get(product_id)
    if not product:
        return not_found_response("Product not found")
    return success_response(product.to_dict_with_reviews())


@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Admin update product."""
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400)

    product = Product.query.get(product_id)
    if not product:
        return not_found_response("Product not found")

    if 'product_name' in data:
        product.product_name = data['product_name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'stock_quantity' in data:
        product.stock_quantity = data['stock_quantity']
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])
    if 'category_id' in data:
        product.category_id = data['category_id']

    try:
        db.session.commit()
        return success_response(product.to_dict(), "Product updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete product."""
    product = Product.query.get(product_id)
    if not product:
        return not_found_response("Product not found")
    try:
        db.session.delete(product)
        db.session.commit()
        return success_response(message="Product deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route('/products/<int:product_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_product_active(product_id):
    """Toggle product active status."""
    product = Product.query.get(product_id)
    if not product:
        return not_found_response("Product not found")
    product.is_active = not product.is_active
    try:
        db.session.commit()
        return success_response(product.to_dict(), f"Product {'activated' if product.is_active else 'deactivated'}")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================
# ORDER MANAGEMENT
# ============================================

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_orders():
    """Get all orders with filters."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    page, per_page = validate_pagination(page, per_page)

    status = request.args.get('status')
    buyer_id = request.args.get('buyer_id', type=int)
    seller_id = request.args.get('seller_id', type=int)
    search = request.args.get('search', type=str)

    query = Order.query
    if status:
        query = query.filter_by(status=status)
    if buyer_id:
        query = query.filter_by(buyer_id=buyer_id)
    if seller_id:
        query = query.filter_by(seller_id=seller_id)

    query = query.order_by(Order.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = [o.to_dict_with_items() for o in pagination.items]
    return paginated_response(orders, page, per_page, pagination.total)


@admin_bp.route('/orders/<int:order_id>', methods=['GET'])
@admin_required
def get_order(order_id):
    """Get full order detail."""
    order = Order.query.get(order_id)
    if not order:
        return not_found_response("Order not found")
    return success_response(order.to_dict_with_history())


@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """Admin override order status."""
    data = request.get_json()
    if not data or not data.get('status'):
        return error_response("Status required", 400)

    order = Order.query.get(order_id)
    if not order:
        return not_found_response("Order not found")

    new_status = data['status']
    old_status = order.status
    order.status = new_status

    history = OrderStatusHistory(
        order_id=order.id,
        status=new_status,
        changed_by=g.current_user_id,
        note=data.get('note', f'Admin override: {old_status} -> {new_status}')
    )
    db.session.add(history)

    if new_status == 'cancelled' and old_status not in ['cancelled', 'refunded']:
        for item in order.items:
            item.product.increase_stock(item.quantity)

    try:
        db.session.commit()
        return success_response(order.to_dict(), "Order status updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================
# CATEGORY MANAGEMENT
# ============================================

@admin_bp.route('/categories', methods=['GET'])
@admin_required
def get_categories():
    """Get all categories with product counts."""
    categories = Category.query.order_by(Category.category_name).all()
    return success_response([c.to_dict_with_product_count() for c in categories])


@admin_bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    """Create category."""
    data = request.get_json()
    if not data or not data.get('category_name'):
        return error_response("Category name required", 400)

    existing = Category.query.filter_by(category_name=data['category_name']).first()
    if existing:
        return error_response("Category already exists", 400)

    try:
        cat = Category(
            category_name=data['category_name'],
            custom_id=data.get('custom_id')
        )
        db.session.add(cat)
        db.session.commit()
        return created_response(cat.to_dict(), "Category created")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@admin_required
def update_category(cat_id):
    """Update category."""
    data = request.get_json()
    cat = Category.query.get(cat_id)
    if not cat:
        return not_found_response("Category not found")

    if 'category_name' in data:
        existing = Category.query.filter(
            Category.category_name == data['category_name'], Category.id != cat_id
        ).first()
        if existing:
            return error_response("Category name already exists", 400)
        cat.category_name = data['category_name']

    try:
        db.session.commit()
        return success_response(cat.to_dict(), "Category updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@admin_required
def delete_category(cat_id):
    """Delete category (only if no products)."""
    cat = Category.query.get(cat_id)
    if not cat:
        return not_found_response("Category not found")

    if cat.products.count() > 0:
        return error_response("Cannot delete category with products", 400)

    try:
        db.session.delete(cat)
        db.session.commit()
        return success_response(message="Category deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================
# PAYMENT MANAGEMENT
# ============================================

@admin_bp.route('/payments', methods=['GET'])
@admin_required
def get_payments():
    """Get all payments."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    page, per_page = validate_pagination(page, per_page)

    status = request.args.get('status')
    method = request.args.get('method')

    query = Payment.query
    if status:
        query = query.filter_by(status=status)
    if method:
        query = query.filter_by(method=method)

    query = query.order_by(Payment.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    payments = [p.to_dict() for p in pagination.items]
    return paginated_response(payments, page, per_page, pagination.total)


@admin_bp.route('/payments/<int:payment_id>/status', methods=['PUT'])
@admin_required
def update_payment_status(payment_id):
    """Update payment status."""
    data = request.get_json()
    if not data or not data.get('status'):
        return error_response("Status required", 400)

    payment = Payment.query.get(payment_id)
    if not payment:
        return not_found_response("Payment not found")

    new_status = data['status']
    if new_status == 'paid':
        payment.mark_paid(data.get('transaction_id'))
    elif new_status == 'failed':
        payment.mark_failed()
    elif new_status == 'refunded':
        payment.mark_refunded()
    else:
        payment.status = new_status

    try:
        db.session.commit()
        return success_response(payment.to_dict(), "Payment status updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================
# REVIEW MANAGEMENT
# ============================================

@admin_bp.route('/reviews', methods=['GET'])
@admin_required
def get_reviews():
    """Get all reviews."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    page, per_page = validate_pagination(page, per_page)

    rating = request.args.get('rating', type=int)
    product_id = request.args.get('product_id', type=int)

    query = ProductReview.query
    if rating:
        query = query.filter_by(rating=rating)
    if product_id:
        query = query.filter_by(product_id=product_id)

    query = query.order_by(ProductReview.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    reviews = [r.to_dict() for r in pagination.items]
    return paginated_response(reviews, page, per_page, pagination.total)


@admin_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@admin_required
def delete_review(review_id):
    """Delete review (moderation)."""
    review = ProductReview.query.get(review_id)
    if not review:
        return not_found_response("Review not found")
    try:
        db.session.delete(review)
        db.session.commit()
        return success_response(message="Review deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================
# ROLES & PERMISSIONS
# ============================================

@admin_bp.route('/roles', methods=['GET'])
@admin_required
def get_roles():
    """Get all roles with permissions."""
    roles = Role.query.all()
    return success_response([r.to_dict_with_permissions() for r in roles])


@admin_bp.route('/permissions', methods=['GET'])
@admin_required
def get_permissions():
    """Get all permissions."""
    perms = Permission.query.all()
    return success_response([p.to_dict() for p in perms])


@admin_bp.route('/user-types', methods=['GET'])
@admin_required
def get_user_types():
    """Get all user types."""
    types = UserType.query.all()
    return success_response([t.to_dict() for t in types])


@admin_bp.route('/governorates', methods=['GET'])
@admin_required
def get_governorates():
    """Get all governorates."""
    govs = Governorate.query.all()
    return success_response([{'id': gov.id, 'gov_name': gov.gov_name} for gov in govs])
