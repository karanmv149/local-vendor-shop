from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'  # Change this in a real app

# --- DATABASE CONFIGURATION ---
# Make sure to update this line with your MySQL password if you have one!
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MySQL%401988@localhost/local_vendor_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'customer' or 'vendor'
    vendor = db.relationship('Vendor', backref='user', uselist=False, cascade="all, delete-orphan")

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shop_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text)
    contact = db.Column(db.String(20))
    timings = db.Column(db.String(100))
    delivery_mode = db.Column(db.String(50), default='Pickup')
    products = db.relationship('Product', backref='vendor', lazy=True, cascade="all, delete-orphan")

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    availability = db.Column(db.Boolean, default=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    status = db.Column(db.String(50), default='Placed')
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_mode = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan")
    customer = db.relationship('User', backref='orders')
    vendor = db.relationship('Vendor', backref='orders')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    product = db.relationship('Product')

# --- AUTHENTICATION DECORATORS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') != role:
                flash(f'You must be a {role} to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- ROUTES ---

@app.route('/')
def index():
    categories = Vendor.query.with_entities(Vendor.category).distinct().all()
    selected_category = request.args.get('category')
    if selected_category:
        vendors = Vendor.query.filter_by(category=selected_category).all()
    else:
        vendors = Vendor.query.all()
    return render_template('index.html', vendors=vendors, categories=[c[0] for c in categories], selected_category=selected_category)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'] # In a real app, hash this!
        role = request.form['role']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(name=name, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        if role == 'vendor':
            new_vendor = Vendor(
                user_id=new_user.id,
                shop_name=request.form['shop_name'],
                category=request.form['category']
            )
            db.session.add(new_vendor)
            db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['name'] = user.name
            session['role'] = user.role
            flash('Logged in successfully!', 'success')
            if user.role == 'vendor':
                return redirect(url_for('vendor_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'vendor':
        return redirect(url_for('vendor_dashboard'))
    else:
        return redirect(url_for('customer_dashboard'))

@app.route('/customer/dashboard')
@login_required
@role_required('customer')
def customer_dashboard():
    orders = Order.query.filter_by(customer_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('customer_dashboard.html', orders=orders)


@app.route('/vendor/dashboard')
@login_required
@role_required('vendor')
def vendor_dashboard():
    vendor = Vendor.query.filter_by(user_id=session['user_id']).first()
    if not vendor:
        flash('Vendor profile not found.', 'danger')
        return redirect(url_for('index'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    orders = Order.query.filter_by(vendor_id=vendor.id).order_by(Order.created_at.desc()).all()
    return render_template('vendor_dashboard.html', vendor=vendor, products=products, orders=orders)

@app.route('/vendor/profile/update', methods=['POST'])
@login_required
@role_required('vendor')
def update_vendor_profile():
    vendor = Vendor.query.filter_by(user_id=session['user_id']).first()
    if vendor:
        vendor.shop_name = request.form['shop_name']
        vendor.address = request.form['address']
        vendor.contact = request.form['contact']
        vendor.timings = request.form['timings']
        vendor.delivery_mode = request.form['delivery_mode']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    return redirect(url_for('vendor_dashboard'))


@app.route('/vendor/product/add', methods=['POST'])
@login_required
@role_required('vendor')
def add_product():
    vendor = Vendor.query.filter_by(user_id=session['user_id']).first()
    if vendor:
        new_product = Product(
            vendor_id=vendor.id,
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            availability='availability' in request.form
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
    return redirect(url_for('vendor_dashboard'))

@app.route('/vendor/product/delete/<int:product_id>')
@login_required
@role_required('vendor')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    vendor = Vendor.query.filter_by(user_id=session['user_id']).first()
    if product.vendor_id == vendor.id:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted!', 'success')
    else:
        flash('You are not authorized to delete this product.', 'danger')
    return redirect(url_for('vendor_dashboard'))

@app.route('/vendor/order/update/<int:order_id>', methods=['POST'])
@login_required
@role_required('vendor')
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    vendor = Vendor.query.filter_by(user_id=session['user_id']).first()
    if order.vendor_id == vendor.id:
        order.status = request.form['status']
        db.session.commit()
        flash(f'Order #{order.id} status updated to {order.status}.', 'success')
    else:
        flash('You are not authorized to update this order.', 'danger')
    return redirect(url_for('vendor_dashboard'))

@app.route('/shop/<int:vendor_id>')
def shop_page(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    products = Product.query.filter_by(vendor_id=vendor.id, availability=True).all()
    return render_template('shop.html', vendor=vendor, products=products)

@app.route('/cart')
@login_required
@role_required('customer')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0
    if cart:
        product_ids = cart.keys()
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        for product in products:
            quantity = cart[str(product.id)]
            item_total = product.price * quantity
            cart_items.append({'product': product, 'quantity': quantity, 'total': item_total})
            total_price += item_total
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
@role_required('customer')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    product = Product.query.get_or_404(product_id)
    product_id_str = str(product_id)
    
    quantity = int(request.form.get('quantity', 1))
    
    # If starting a new cart or switching vendors, clear old cart
    if 'cart_vendor_id' not in session or session['cart_vendor_id'] != product.vendor_id:
        cart = {}
        session['cart_vendor_id'] = product.vendor_id
    
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity

    session['cart'] = cart
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('shop_page', vendor_id=product.vendor_id))

@app.route('/cart/remove/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        session['cart'] = cart
        # If cart is empty, remove vendor lock
        if not cart:
            session.pop('cart_vendor_id', None)
    return redirect(url_for('view_cart'))


@app.route('/order/place', methods=['POST'])
@login_required
@role_required('customer')
def place_order():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('view_cart'))

    delivery_mode = request.form['delivery_mode']
    vendor_id = session.get('cart_vendor_id')

    total_price = 0
    order_items_data = []
    product_ids = [int(k) for k in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    for product in products:
        quantity = cart[str(product.id)]
        price = product.price
        total_price += price * quantity
        order_items_data.append({'product_id': product.id, 'quantity': quantity, 'price': price})

    new_order = Order(
        customer_id=session['user_id'],
        vendor_id=vendor_id,
        total_price=total_price,
        delivery_mode=delivery_mode
    )
    db.session.add(new_order)
    db.session.commit()

    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # Clear the cart
    session.pop('cart', None)
    session.pop('cart_vendor_id', None)

    flash('Order placed successfully!', 'success')
    return redirect(url_for('customer_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)