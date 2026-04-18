# 🛒 Ecommerce Backend API (Django)

## 📌 Project Overview
This is a complete Ecommerce Backend API built using Django and Django REST Framework.
It includes product management, cart system, order processing, payment simulation, and user authentication.

-------
## 🚀 Features
### 🔐 Authentication
* User Registration
* Login / Logout
* Token-based authentication

### 📦 Product System
* Create Product
* Product List API
* Product Detail API

### 🛒 Cart System
* Add to Cart
* Quantity management
* Stock validation (out of stock / not enough stock)

### 📑 Order System
* Create Order from Cart
* View User Orders
* Order Details
* Cancel Order
* Update Order Status

### 💳 Payment System
* Fake Payment API
* is_paid field management

### 🔍 Search & Filter
* Search products by name
* Filter by price range

### 📄 Pagination
* Custom pagination system

-----
## 🛠️ Technologies Used
* Python
* Django
* Django REST Framework
* SQLite (Default DB)

-----
## 🔗 API Endpoints
### 🔐 Auth
* POST `/api/register/`
* POST `/api/api_login/`

### 📦 Products
* GET `/api/products/`
* GET `/api/product/<id>/`
* POST `/api/product/create/`

### 🛒 Cart
* POST `/api/cart/add/`

### 📑 Orders
* POST `/api/order/create/`
* GET `/api/my-orders/`
* GET `/api/order/<id>/`
* PUT `/api/order/<id>/update-status/`
* POST `/api/order/<id>/cancel/`
* POST `/api/order/<id>/pay/`

---

## ⚙️ Setup Instructions
```bash
git clone https://github.com/your-username/ecommerce-backend-api.git
cd ecommerce-backend-api
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

-----
## 🧪 Testing
You can test all APIs using Postman.

## 🎯 Project Goal
This project was built for learning and practicing backend development, including real-world ecommerce logic.

-----
## 👨‍💻 Author
Abdul Hakim
Backend Developer (Django)
