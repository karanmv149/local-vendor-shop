-- Create the database
CREATE DATABASE IF NOT EXISTS local_vendor_db;
USE local_vendor_db;

-- Table: users
-- Stores both customer and vendor login details.
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'vendor') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: vendors
-- Stores vendor-specific shop details, linked to a user.
CREATE TABLE vendors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    shop_name VARCHAR(255) NOT NULL,
    category ENUM('Groceries', 'Fruits', 'Vegetables', 'Bakery', 'Stationery', 'Medical', 'Tiffin', 'Tailoring') NOT NULL,
    address TEXT,
    contact VARCHAR(20),
    timings VARCHAR(100),
    delivery_mode ENUM('Pickup', 'Vendor Delivery', 'Both') DEFAULT 'Pickup',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: products
-- Stores products, linked to a vendor.
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    availability BOOLEAN DEFAULT TRUE,
    image VARCHAR(255), -- Optional: path to image
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
);

-- Table: orders
-- Stores customer orders.
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    vendor_id INT NOT NULL,
    status ENUM('Placed', 'Accepted', 'Out for Delivery', 'Delivered', 'Rejected') NOT NULL DEFAULT 'Placed',
    total_price DECIMAL(10, 2) NOT NULL,
    delivery_mode ENUM('Pickup', 'Vendor Delivery') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
);

-- Table: order_items
-- Stores individual items within an order (junction table).
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL, -- Price at the time of order
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- --- SAMPLE DATA ---

-- Users
INSERT INTO users (name, email, password, role) VALUES
('Alice (Customer)', 'customer@example.com', 'password123', 'customer'),
('Bob (Vendor)', 'vendor@example.com', 'password123', 'vendor'),
('Charlie (Vendor)', 'vendor2@example.com', 'password123', 'vendor');

-- Vendors
INSERT INTO vendors (user_id, shop_name, category, address, contact, timings, delivery_mode) VALUES
(2, 'Bob\'s Fresh Groceries', 'Groceries', '123 Market St, Townsville', '9876543210', '9 AM - 8 PM', 'Both'),
(3, 'Charlie\'s Stationery', 'Stationery', '456 Paper Lane, Townsville', '9876512345', '10 AM - 6 PM', 'Pickup');

-- Products for Bob's Groceries (vendor_id = 1)
INSERT INTO products (vendor_id, name, description, price, availability) VALUES
(1, 'Organic Apples', 'Fresh, juicy organic apples.', 150.00, TRUE),
(1, 'Whole Wheat Bread', 'Healthy and delicious whole wheat bread.', 40.00, TRUE),
(1, 'Fresh Milk (1L)', 'Pasteurized fresh cow milk.', 55.00, FALSE);

-- Products for Charlie's Stationery (vendor_id = 2)
INSERT INTO products (vendor_id, name, description, price, availability) VALUES
(2, 'Notebook Set (Pack of 5)', 'A5 size, 200 pages ruled.', 250.00, TRUE),
(2, 'Blue Gel Pens (Pack of 10)', 'Smooth writing gel pens.', 100.00, TRUE);