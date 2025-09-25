# Dukaan - Local Vendor Hub 🛍️

Dukaan is a full-stack web application designed to connect local customers with nearby vendors. It provides a seamless platform for vendors to manage their digital storefront and for customers to browse, order, and track items from shops in their community.



---

## ✨ Key Features

### For Customers:
- **User Authentication:** Secure sign-up and login for a personalized experience.
- **Shop Discovery:** Browse local shops filtered by categories.
- **Product Viewing:** View detailed product listings for each shop.
- **Shopping Cart:** Add items to a cart, which intelligently handles items from one vendor at a time.
- **Order Placement:** Place orders with options for "In-Store Pickup" or "Vendor Delivery".
- **Order Tracking:** A personal dashboard to view order history and track the status in real-time (Placed → Accepted → Out for Delivery → Delivered).

### For Vendors:
- **Vendor Registration:** Easily sign up as a vendor and set up a shop profile.
- **Shop Management:** Update shop details like name, address, contact info, and timings.
- **Product Management:** Add, update, and delete products from the shop inventory.
- **Order Management:** View incoming customer orders and update their status.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite (or can be configured for PostgreSQL/MySQL)
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Templating:** Jinja2
- **Animations:** AOS (Animate on Scroll) Library

---

## 🚀 Setup and Installation

Follow these steps to get the project running on your local machine.

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/karanmv149/Dukaan-E-Commerce-Platform.git](https://github.com/karanmv149/Dukaan-E-Commerce-Platform.git)
    cd Dukaan-E-Commerce-Platform
    ```

2.  **Create a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database:**
    Open a Python shell in your terminal and run the following commands to create the database tables.
    ```python
    from app import app, db
    with app.app_context():
        db.create_all()
    ```

5.  **Run the Application:**
    ```bash
    flask run
    ```
    The application will be running at `http://127.0.0.1:5000`.

---

## 📖 How to Use

1.  **Sign Up:** Create an account as either a "Customer" or a "Vendor".
2.  **If you are a Vendor:**
    - You will be redirected to your dashboard.
    - Update your shop profile with your address and timings.
    - Add products to your inventory.
    - Wait for orders to come in!
3.  **If you are a Customer:**
    - Browse shops from the homepage.
    - Visit a shop and add products to your cart.
    - View your cart and proceed to confirm your order.
    - Track the status of your order in your dashboard.


To test all the features, use the sample accounts we created in the database:

Log in as a Customer:
Email: customer@example.com
Password: password123

Log in as a Vendor:
Email: vendor@example.com
Password: password123

