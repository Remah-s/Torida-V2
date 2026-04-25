# Torida B2B Marketplace - Features & Libraries

## 📚 Libraries & Dependencies Used
The backend is built with Python and utilizes the following libraries (as defined in `requirements.txt`):

1. **Flask (3.0.3)**: The core web framework used for routing and handling HTTP requests.
2. **Flask-SQLAlchemy (3.1.1)**: ORM (Object-Relational Mapping) used for all database interactions and schema definitions.
3. **Flask-CORS (4.0.1)**: Middleware to handle Cross-Origin Resource Sharing, allowing frontend applications to interact with the API securely.
4. **mysql-connector-python (8.4.0)**: The official MySQL driver for Python, allowing SQLAlchemy to communicate with the MySQL database.
5. **bcrypt (4.1.3)**: Used for secure password hashing and verification.
6. **python-dotenv (1.0.1)**: Loads configuration environments (like database URIs, JWT secrets) from a `.env` file into system environment variables.
7. **PyJWT (2.8.0)**: JSON Web Token implementation used for generating and verifying secure access and refresh tokens for user authentication.

---

## 🚀 Application Features

### 1. User Authentication & Security
- **JWT Authentication**: Secure login system providing both short-lived access tokens and refresh tokens.
- **OTP Verification**: Email verification and password resets using a time-sensitive One-Time Password (OTP) system.
- **Password Hashing**: Secure storage of user passwords using `bcrypt`.
- **Role-Based Access Control (RBAC)**: Fine-grained permissions (e.g., `create_products`, `manage_roles`) mapped to roles (Admin, Manager, Editor, Viewer).

### 2. Multi-Type User Management
- **User Types**: Explicit separation of capabilities between:
  - **Suppliers & Companies** (`can_sell=True`): Can list products and manage incoming orders.
  - **Retailers** (`can_buy=True`): Can browse products, manage carts, and place orders.
- **Business Profiles**: Sellers can maintain business details including Tax Numbers and Commercial Registration information.
- **Address Book**: Users can manage multiple delivery/shipping addresses.

### 3. Product Catalog & Inventory
- **Product Management**: Sellers can create, update, and delete product listings.
- **Image handling**: Support for multiple product images, including setting a "primary" image. 
- **Dynamic Coding**: Auto-generation of unique, sequential serial codes for products based on their category (e.g., `PRD-001001`).
- **Inventory Tracking**: Products have a `stock_quantity` that is automatically verified before purchase and deducted upon order creation.
- **Search & Filtering**: Comprehensive querying of products by category, seller, price range, active status, and textual search.

### 4. Shopping Cart & Order Splitting
- **Persistent Carts**: Retailers have persistent shopping carts tied to their accounts.
- **Multi-Seller Checkout**: The system automatically groups cart items by seller. During checkout, one cart is intelligently split into multiple, distinct `Order` records (one for each supplier involved).

### 5. Comprehensive Order Tracking
- **Order Lifecycle**: Orders transition through well-defined states: `Pending -> Confirmed -> Processing -> Shipped -> Out for Delivery -> Delivered -> Refunded` (or `Cancelled`).
- **Status History**: Every status transition is logged in the `OrderStatusHistory` table with the user ID who made the change and an optional note.
- **Stock Restoration**: If an order is cancelled, the system automatically restores the stock quantities for those products.

### 6. Payments System
- **Payment Methods**: Support for Cash, Credit Card, Bank Transfer, and Wallet methods.
- **Payment Lifecycle**: Structured tracking of payment intents (`unpaid`, `paid`, `failed`, `refunded`) linked to specific transactions.

### 7. Notification & Email Services
- **Automated Emails**: An internal `EmailService` sends rich HTML emails for Welcome messages, OTP codes, and Order Confirmations.
- **System Notifications**: An internal `NotificationService` that tracks important business events (e.g., payment successes, order status updates) to alert users in real-time or within the app.
