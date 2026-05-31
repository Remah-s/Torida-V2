# TORIDA B2B Marketplace - System Implementation & Testing Report

**Date:** May 14, 2026  
**Project:** TORIDA Backend API  
**Technology Stack:** Python 3.9+, Flask, MySQL 8.0+, SQLAlchemy

---

## 1. System Implementation Architecture

The Torida backend is designed as a robust, scalable RESTful API catering to a B2B marketplace in Egypt. It is structured using the Factory Pattern and Blueprint routing for modularity.

### 1.1 Core Modules & Structure
The application follows a clean, service-oriented architecture:
*   **`app/__init__.py`**: Utilizes the Flask Application Factory pattern, ensuring safe database binding and configuration management.
*   **`app/models/`**: Contains 24 distinct SQLAlchemy models defining the relational database schema. Major entities include `User`, `Product`, `Order`, `Cart`, `Category`, and `BusinessProfile`.
*   **`app/routes/`**: Contains 16 Blueprint modules, mapping HTTP requests to their corresponding logic.
*   **`app/services/`**: Abstracts complex business operations (e.g., `email_service`, `otp_service`, `notification_service`) away from the routing layer, promoting reusability.
*   **`app/utils/`**: Shared utilities for standardizing JSON responses, input validation, and JWT token manipulation.

### 1.2 Security & Authentication
*   **Stateless Authentication**: Uses JSON Web Tokens (JWT) for secure session management. Access tokens handle short-lived authorizations, while refresh tokens handle session longevity.
*   **Role-Based Access Control (RBAC)**: Fine-grained permissions and roles (Supplier, Retailer, Company) restrict endpoints. For example, only Suppliers/Companies can create products, while Retailers manage shopping carts.
*   **OTP Verification**: Used for secure user onboarding (Email Verification) and account recovery (Password Reset).

### 1.3 Database Design
The MySQL schema consists of 24 interlinked tables:
*   **Users & Profiles**: `users`, `roles`, `permissions`, `business_profiles`, `user_types`
*   **E-Commerce Core**: `products`, `categories`, `product_images`, `product_reviews`
*   **Transactions**: `orders`, `order_items`, `order_status_history`, `payments`, `carts`, `wishlists`
*   **System Assets**: `governorates`, `notifications`, `code_sequences`

---

## 2. Testing Methodology & Framework

The system utilizes a dual testing approach: programmatic integration testing via Python, and automated API lifecycle testing via Postman.

### 2.1 Python Integration Test Suite (`test_all_apis.py`)
A comprehensive, custom-built local test suite executes end-to-end integration flows.
*   **Coverage**: Tests 17 distinct functional blocks (Root/Health, Public, Auth, Users, Categories, Products, Cart, Wishlist, Addresses, Orders, Payments, Reviews, Notifications, Roles, Profiles).
*   **Workflow Automation**: Mimics real user journeys. For example: Registers a supplier $\rightarrow$ Logs in $\rightarrow$ Creates category $\rightarrow$ Creates product $\rightarrow$ Registers retailer $\rightarrow$ Adds product to cart $\rightarrow$ Checks out $\rightarrow$ Processes payment.
*   **State Management**: Automatically extracts dynamically generated IDs (like `test_product_id`, `test_order_id`, `access_token`) from JSON responses and injects them into subsequent test requests.
*   **Cleanup**: Features a dedicated teardown phase (Phase 17) to delete test records, ensuring the database remains clean across test runs.

### 2.2 Postman Automated Collection
The `torida_postman_collection.json` serves as both interactive documentation and an automated assertion framework. Recent fixes have brought the collection to a **100% pass rate** across 92 assertions.

*   **Pre-request Scripts**: A collection-level script checks for empty `{{token}}` variables and performs an auto-login sequence using injected test credentials before executing protected requests.
*   **ID Chaining Framework**: Test scripts on `POST` endpoints automatically capture resource IDs (e.g., `{{product_id}}`) and save them to the environment. This entirely removes the need for manual ID copying and eliminates `404 Resource Not Found` errors during testing.
*   **Environment Management**: Dynamic variables (`base_url`, `token`, `test_email`, `test_password`) allow seamless switching between local, staging, and production environments.

### 2.3 Database Seeding
To ensure test reliability and consistency, `seed_database.py` was implemented.
*   Populates a fresh database with the necessary taxonomy (Governorates, Categories, User Types, Roles).
*   Generates reliable test accounts (e.g., `john.doe@example.com`) that Postman scripts rely on for the auto-login sequences.

---

## 3. Conclusion

The system implementation is highly modular, separating routing, database mapping, and business logic. The testing infrastructure is equally robust. By combining a fully automated Python execution script for CI/CD checks and an ID-chained Postman collection for manual and developer testing, the Torida API ensures high reliability, strict security, and excellent developer experience.
