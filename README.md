# TORIDA - B2B Marketplace Backend

A complete Flask-based REST API backend for a B2B marketplace platform in Egypt.

## 🚀 Features

### User Management
- **User Types**: Supplier (can sell), Retailer (can buy), Company (can sell)
- **Authentication**: JWT-based authentication with access and refresh tokens
- **OTP Verification**: Email verification and password reset via OTP
- **Role-Based Access Control**: Flexible roles and permissions system

### Product Management
- **Categories**: Hierarchical product categorization
- **Products**: Full CRUD with image management
- **Search & Filtering**: Advanced product search and filtering
- **Stock Management**: Real-time inventory tracking

### Order System
- **Orders**: Complete order lifecycle management
- **Order Status Tracking**: Detailed status history
- **Multi-seller Orders**: Automatic order splitting by seller
- **Notifications**: Real-time order updates

### Additional Features
- **Shopping Cart**: Cart management for retailers
- **Wishlist**: Product wishlist functionality
- **Reviews**: Product rating and review system
- **Addresses**: Multiple shipping address management
- **Payments**: Payment processing simulation

## 📁 Project Structure

```
torida/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py             # Configuration settings
│   ├── database.py           # Database initialization
│   ├── .env                  # Environment variables
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── ... (24 models total)
│   ├── routes/               # API route blueprints
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── user_routes.py
│   │   └── ... (16 blueprints total)
│   ├── services/             # Business logic services
│   │   ├── email_service.py
│   │   ├── otp_service.py
│   │   └── notification_service.py
│   └── utils/                # Utility functions
│       ├── response.py
│       ├── validators.py
│       ├── auth.py
│       └── helpers.py
├── uploads/                  # File uploads directory
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- MySQL 8.0+

### Setup

1. **Clone the repository**
   ```bash
   cd /home/z/my-project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Edit `app/.env` with your settings:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=torida
   DB_USER=root
   DB_PASSWORD=your_password
   ```

5. **Create database**
   ```sql
   CREATE DATABASE torida;
   ```

6. **Initialize database**
   ```bash
   flask init-db
   flask seed-db
   ```

7. **Run the server**
   ```bash
   python run.py
   ```

## 📡 API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | User login |
| POST | `/logout` | User logout |
| POST | `/refresh` | Refresh access token |
| POST | `/verify-email` | Verify email with OTP |
| POST | `/forgot-password` | Request password reset |
| POST | `/reset-password` | Reset password with OTP |
| POST | `/change-password` | Change password |
| GET | `/me` | Get current user |

### Users (`/api/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all users |
| GET | `/<id>` | Get user by ID |
| PUT | `/<id>` | Update user |
| DELETE | `/<id>` | Deactivate user |
| GET | `/<id>/roles` | Get user roles |
| POST | `/<id>/roles` | Assign role |
| DELETE | `/<id>/roles/<role_id>` | Remove role |

### Products (`/api/products`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List products (filterable) |
| GET | `/<id>` | Get product details |
| POST | `/` | Create product (sellers only) |
| PUT | `/<id>` | Update product |
| DELETE | `/<id>` | Delete product |
| GET | `/<id>/images` | Get product images |
| POST | `/<id>/images` | Add product image |
| GET | `/my-products` | Get seller's products |

### Orders (`/api/orders`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List orders |
| GET | `/<id>` | Get order details |
| POST | `/` | Create order from cart |
| PUT | `/<id>/status` | Update order status |
| POST | `/<id>/cancel` | Cancel order |
| GET | `/<id>/items` | Get order items |
| GET | `/<id>/history` | Get status history |

### Cart (`/api/cart`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Get cart |
| POST | `/items` | Add item to cart |
| PUT | `/items/<id>` | Update item quantity |
| DELETE | `/items/<id>` | Remove item |
| DELETE | `/` | Clear cart |

### Other Endpoints
- **Categories**: `/api/categories`
- **Wishlist**: `/api/wishlist`
- **Payments**: `/api/payments`
- **Reviews**: `/api/reviews`
- **Notifications**: `/api/notifications`
- **Addresses**: `/api/addresses`
- **Roles**: `/api/roles`
- **Permissions**: `/api/permissions`
- **Governorates**: `/api/governorates`
- **User Types**: `/api/user-types`
- **Business Profiles**: `/api/business-profiles`

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Getting a Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Using the Token
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## 📊 Database Schema

The database consists of 24 tables:

1. **governorates** - Egyptian governorates
2. **user_types** - User type definitions (Supplier, Retailer, Company)
3. **roles** - User roles
4. **permissions** - Permission definitions
5. **role_permissions** - Role-permission associations
6. **code_sequences** - User code generation sequences
7. **users** - User accounts
8. **user_roles** - User-role associations
9. **business_profiles** - Business information
10. **otps** - One-time passwords
11. **addresses** - User addresses
12. **categories** - Product categories
13. **product_sequences** - Product code sequences
14. **products** - Product listings
15. **product_images** - Product images
16. **orders** - Customer orders
17. **order_items** - Order line items
18. **order_status_history** - Order status changes
19. **payments** - Payment records
20. **product_reviews** - Product reviews
21. **carts** - Shopping carts
22. **cart_items** - Cart line items
23. **wishlists** - User wishlists
24. **notifications** - User notifications

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 3306 |
| `DB_NAME` | Database name | torida |
| `DB_USER` | Database user | root |
| `DB_PASSWORD` | Database password | |
| `SECRET_KEY` | Flask secret key | |
| `JWT_SECRET_KEY` | JWT signing key | |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access token expiry (seconds) | 86400 |
| `JWT_REFRESH_TOKEN_EXPIRES` | Refresh token expiry (seconds) | 2592000 |
| `MAIL_SERVER` | SMTP server | smtp.gmail.com |
| `MAIL_PORT` | SMTP port | 587 |
| `MAIL_USERNAME` | SMTP username | |
| `MAIL_PASSWORD` | SMTP password | |

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 📝 License

MIT License

## 👥 Authors

TORIDA Development Team
