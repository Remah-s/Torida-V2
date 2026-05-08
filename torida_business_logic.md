# Torida B2B Marketplace - Business and Sequence Logic

## 1. User & Authentication Logic
### Business Rules:
- **User Types**: There are multiple user types such as Suppliers (can\_sell=True), Companies (can\_sell=True), and Retailers (can\_buy=True).
- **Registration**: 
  - Required fields: full name, phone, email, password, user type, and governorate.
  - Generates a unique `code` and `custom_id` based on the user type and governorate (e.g., `SUP-123001` for suppliers, `RET-123002` for retailers).
  - Sends a welcome email upon successful registration.
  - Automatically generates and sends an OTP for email account verification.
  - Returns access and refresh JWT tokens immediately for login.
- **Login**: Verifies credentials and user's active status. Returns both access and refresh tokens.
- **Email Verification & Password Reset**: Relies on OTPs. Users provide their email/OTP to verify account or change passwords.

### Registration Sequence Flow:
1. Client sends POST `/api/auth/register` with user details.
2. Server validates input (email format, phone format, password strength) and checks for duplicates.
3. Server looks up `CodeSequence` for the specific `type_id` and `gov_id` to generate a sequential `custom_id` & `code`.
4. Server creates the [User](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/user.py#10-124) in the database with a hashed password.
5. [EmailService](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/services/email_service.py#13-354) sends a welcome email.
6. [OTPService](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/services/otp_service.py#14-113) generates an OTP and sends it via email/SMS for verification.
7. Server generates JWT tokens (`access_token`, [refresh_token](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/routes/auth_routes.py#184-216)).
8. Server returns HTTP 201 Created with user data and tokens.

---

## 2. Product Management Logic
### Business Rules:
- **Authorization**: Only users with `can_sell=True` (Suppliers, Companies) can create, update, or delete products.
- **Product Entity**: Contains custom IDs (e.g., `PRD-001001` based on category), name, description, price, and stock quantity.
- **Images**: Products can have multiple images, one of which can be marked as the [primary](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/routes/product_routes.py#351-384) image. Only the seller can manage their product images.
- **Visibility**: Products are tied to a specific `category_id` and `company_id` (the seller).

### Product Creation Sequence Flow:
1. Seller sends POST `/api/products` with category, name, price, and stock quantity.
2. Server validates the seller's permissions ([can_sell](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/user.py#114-117) check).
3. Server retrieves or initializes the `ProductSequence` for the given category to generate a unique product code.
4. Server creates the [Product](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/product.py#10-111) associated with the seller.
5. Server returns HTTP 201 Created with product data.
6. (Optional) Seller can subsequently upload images via POST `/api/products/{id}/images`.

---

## 3. Cart & Order Logic
### Business Rules:
- **Cart**: Associated one-to-one with a user. Retailers add products to their carts.
- **Order Placement Requirement**: Only Retailers (`can_buy=True`) can place orders.
- **Order Splitting**: If a retailer's cart contains items from multiple different sellers, the system splits the cart into **multiple separate orders** (one order per seller).
- **Stock Management**: Upon order creation, product stock is immediately reduced. If an order is cancelled, the stock is restored.
- **Order Status Flow**: Pending -> Confirmed -> Processing -> Shipped -> Out for Delivery -> Delivered -> Refunded. (Can be Cancelled from Pending/Confirmed states).
- **Status Authorization**: 
  - Both buyers and sellers can cancel an order (if in an allowed state).
  - Only sellers can advance the status (e.g., Confirmed, Shipped, Delivered).

### Order Creation Sequence Flow:
1. Retailer builds a [Cart](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/cart.py#10-61) with items.
2. Retailer sends POST `/api/orders` to checkout.
3. Server verifies the user is a Retailer ([can_buy](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/user.py#118-121)).
4. Server groups cart items by `seller_id`.
5. For each seller, the server:
   - Verifies product stock.
   - Creates a new [Order](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/order.py#10-111) object (status=`pending`).
   - Copies cart items to `OrderItem` objects.
   - Reduces the `stock_quantity` of each product.
   - Calculates the `total_price`.
   - Records an `OrderStatusHistory` entry.
   - Uses `NotificationService` to notify the seller of a pending order.
6. Server clears the `CartItems`.
7. [EmailService](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/services/email_service.py#13-354) sends an order confirmation email to the buyer.
8. Server returns HTTP 201 with the created order(s).

---

## 4. Payment Logic
### Business Rules:
- **Payment Lifecycle**: Tied one-to-one to an [Order](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/order.py#10-111). Options include Cash, Credit Card, Bank Transfer, and Wallet.
- **Status**: Default is `unpaid`. Can transition to [paid](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/payment.py#61-67), [failed](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/payment.py#68-71), or [refunded](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/payment.py#72-75).
- **Authorization**: Only buyers can process (pay) a payment. Only sellers (or admins) can refund a payment.

### Payment Processing Sequence Flow:
1. Buyer sends POST `/api/payments` to create a payment intent.
2. Server validates the buyer.
3. Server creates a [Payment](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/payment.py#10-78) object linked to the [Order](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/order.py#10-111) with status `unpaid`.
4. Buyer sends POST `/api/payments/{id}/pay` with transaction details.
5. Server validates payment state (ensures it's not already paid/refunded).
6. Server marks the payment as [paid](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/payment.py#61-67), sets the `transaction_id`, and records `paid_at`.
7. Server automatically updates the associated [Order](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/models/order.py#10-111) status to `confirmed` (if it was `pending`).
8. `NotificationService` notifies the seller about the successful payment.

---

## Technical Architectural Summary
- **Database**: Relational database (models interact via SQLAlchemy ORM).
- **Token Based Auth**: JWT is used for authorization (access and refresh tokens). Decorators like `@token_required` identify the user.
- **Extensibility**: Uses blueprints for horizontal scaling of route concepts (Auth, Products, Orders, Payments, Users, Business Profiles).
- **Integrations**: Has service layers ([EmailService](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/services/email_service.py#13-354), [OTPService](file:///c:/Users/COMPUMARTS/Downloads/torida_backend_complete/app/services/otp_service.py#14-113), `NotificationService`) that mock or handle external side-effects outside the core request-response cycle.
