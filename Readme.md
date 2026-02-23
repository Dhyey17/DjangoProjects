# Inventory Management System — Django REST API
A backend REST API built with **Django** and **Django REST Framework** for managing sellers, products, and orders. 

## 🚀 Tech Stack
- Language: Python
- Framework: Django 6.0.2
- API Layer: Django Rest Framework
- Database: Sqlite3
- File Storage: Django default(locally)

## ⚙️ Setup & Installation

### 1. Clone the repository
```terminaloutput
git clone https://github.com/Dhyey17/DjangoProjects.git
cd InventoryManagementSystemDjango
```

### 2. Create and activate a virtual environment
```terminaloutput
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```terminaloutput
pip install -r requirements.txt
```

> **Note:** `Pillow` is required for `ImageField` support on the Products model.

### 4. Run migrations
```terminaloutput
python manage.py migrate
```

### 5. Start the development server
```terminaloutput
python manage.py runserver
```

The API will be live at `http://127.0.0.1:8000/`

---

## 🔐 Authentication

This API uses **JWT (JSON Web Token)** based authentication. Tokens are generated at login and must be included in subsequent protected requests.

**Header format:**
```
Authorization: Bearer <your_token>
```

Tokens expire after **30 minutes** by default.

---

## 📡 API Endpoints

### 👤 Sellers (`/sellers/`)

| Method | Endpoint              | Auth Required | Description              |
|--------|-----------------------|---------------|--------------------------|
| GET    | `/sellers/`           | ❌            | List all sellers          |
| POST   | `/sellers/`           | ❌            | Register a new seller     |
| GET    | `/sellers/<id>`       | ❌            | Get a seller's details    |
| PATCH  | `/sellers/<id>`       | ✅ (own only) | Update seller info        |
| DELETE | `/sellers/<id>`       | ✅ (own only) | Soft-delete a seller      |
| POST   | `/sellers/login`      | ❌            | Login and get JWT token   |
| GET    | `/sellers/<id>/products` | ❌         | Get products by seller    |

---

### 📦 Products (`/products/`)

| Method | Endpoint           | Auth Required | Description              |
|--------|--------------------|---------------|--------------------------|
| GET    | `/products/`       | ❌            | List all products         |
| POST   | `/products/`       | ✅            | Create a new product      |
| GET    | `/products/<id>/`  | ❌            | Get product details       |
| PATCH  | `/products/<id>/`  | ✅            | Update a product          |
| DELETE | `/products/<id>/`  | ✅            | Soft-delete a product     |

**Create/Update Product — form-data fields:**

| Field      | Type    | Required | Notes                         |
|------------|---------|----------|-------------------------------|
| `name`     | string  | ✅       |                               |
| `price`    | float   | ✅       |                               |
| `quantity` | integer | ✅       |                               |
| `category` | string  | ✅       |                               |
| `expiry`   | date    | ❌       | Format: `YYYY-MM-DD`          |
| `image`    | file    | ❌       | Uploaded to `/media/products/` |

---

### 🛒 Orders (`/orders/`)

| Method | Endpoint         | Auth Required | Description                |
|--------|------------------|---------------|----------------------------|
| POST   | `/orders/`       | ✅            | Create a new order          |
| GET    | `/orders/`       | ✅            | List all orders for seller  |
| GET    | `/orders/<id>/`  | ✅            | Get a specific order        |

**Create Order — JSON body:**

```json
{
  "type": "INCOMING",
  "items": [
    {
      "product_id": 1,
      "quantity": 10
    }
  ]
}
```

- `type` must be `"INCOMING"` or `"OUTGOING"`
- `INCOMING` → increases product stock
- `OUTGOING` → decreases product stock (validates sufficient quantity before proceeding)
- `total_price` is auto-calculated from `price_at_time × quantity` per item

---

## 🗃️ Data Models

### Sellers
| Field        | Type        | Notes                        |
|--------------|-------------|------------------------------|
| `id`         | AutoField   | Primary key                  |
| `name`       | CharField   |                              |
| `username`   | CharField   | Unique                       |
| `password`   | CharField   | Stored as Django hash        |
| `is_deleted` | BooleanField| Soft delete flag             |

### Products
| Field        | Type         | Notes                                |
|--------------|--------------|--------------------------------------|
| `id`         | BigAutoField | Primary key                          |
| `seller`     | ForeignKey   | References `Sellers`                 |
| `name`       | CharField    |                                      |
| `price`      | FloatField   |                                      |
| `quantity`   | IntegerField |                                      |
| `expiry`     | DateField    | Nullable                             |
| `category`   | CharField    |                                      |
| `image`      | ImageField   | Nullable, uploaded to `products/`    |
| `is_deleted` | BooleanField | Soft delete flag                     |

### Orders
| Field        | Type         | Notes                          |
|--------------|--------------|--------------------------------|
| `id`         | BigAutoField | Primary key                    |
| `seller`     | ForeignKey   | References `Sellers`           |
| `type`       | CharField    | `INCOMING` or `OUTGOING`       |
| `total_price`| FloatField   | Auto-calculated                |
| `timestamp`  | DateTimeField| Auto-set on creation           |

### OrderItems
| Field           | Type         | Notes                          |
|-----------------|--------------|--------------------------------|
| `id`            | BigAutoField | Primary key                    |
| `order`         | ForeignKey   | References `Orders`            |
| `product`       | ForeignKey   | References `Products`          |
| `quantity`      | IntegerField |                                |
| `price_at_time` | FloatField   | Snapshot of price at order time|
| `total`         | FloatField   | Auto-calculated on save        |

---

## 🛠️ Core Utilities (`core/utils.py`)

A shared utilities module used across all apps:

| Function                  | Purpose                                          |
|---------------------------|--------------------------------------------------|
| `success_response()`      | Returns a standardized success JSON response     |
| `error_response()`        | Returns a standardized error JSON response       |
| `generate_jwt()`          | Creates a signed JWT for a seller                |
| `decode_jwt()`            | Decodes and validates a JWT                      |
| `get_user_from_request()` | Extracts and validates the seller from the token |
| `validate_order_type()`   | Validates order type is INCOMING or OUTGOING     |
| `validate_items()`        | Validates the items list in an order request     |
| `process_order_items()`   | Creates OrderItems and updates product stock     |

**Standard Response Format:**

Success:
```json
{
  "success": true,
  "msg": "...",
  "data": { }
}
```

Error:
```json
{
  "success": false,
  "msg": "..."
}
```

---
