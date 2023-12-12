import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as user_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from models.cart import Cart
from models.farmers import Farmer
from models.consumers import add_consumer, Consumer
from models.engine.storage import DatabaseStorage
from models.products import Product
from models.orders import Order

app = Flask(__name__)
app.secret_key = 'hl_user_session'

# Initialize the DatabaseStorage
db_storage = DatabaseStorage()


@app.route('/')
def index():
    # get all products
    products = (
        db_storage.get_session()
        .query(Product, Farmer)
        .join(Farmer, Product.farmer_id == Farmer.id)
        .all()
    )
    if 'user_id' in user_session:
        return render_template('index.html',
                               name=user_session['user_name'],
                               email=user_session['user_email'],
                               id=user_session['user_id'],
                               authenticated=user_session['authenticated'],
                               products=products)

    return render_template('index.html', products=products)


@app.route('/register')
def register_farmer():
    return render_template('register.html')


@app.route('/save', methods=['POST'])
def save():
    u_id = str(uuid.uuid4())
    acc = request.form['account-type']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    location = request.form['location']
    password = request.form['password']

    # Create a session to interact with the database
    session = db_storage.get_session()

    if acc == "farmer":
        # Add the farmer to the 'farmers' table
        Farmer.add_farmer(session, u_id, name, email, phone,
                          location, password)
        return redirect(url_for('dashboard'))
    elif acc == "consumer":
        # Add the consumer to the 'consumers' table
        add_consumer(session, u_id, name, email, phone,
                     location, password)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the email and password from the form
        email = request.form.get('email')
        password = request.form.get('password')

        # Perform authentication
        farmer = authenticate_farmer(email, password)

        if farmer:
            user_session['authenticated'] = True
            user_session['user_id'] = farmer.id
            user_session['user_name'] = farmer.name
            user_session['user_email'] = farmer.email
            return redirect(url_for('dashboard'))
        else:
            consumer = authenticate_consumer(email, password)
            if consumer:
                user_session['authenticated'] = True
                user_session['user_id'] = consumer.id
                user_session['user_name'] = consumer.name
                user_session['user_email'] = consumer.email
                return redirect(url_for('index'))
            else:
                flash("Incorrect credentials", 'error')

    return render_template('login.html')


# Add a route to handle logout
@app.route('/logout')
def logout():
    # Clear the session data
    user_session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' in user_session:
        # Get the authenticated farmer
        authenticated_farmer = (db_storage.get_session().query(Farmer)
                                .filter_by(id=user_session['user_id']).first())
        if authenticated_farmer:
            # Get the products added by the farmer
            products = authenticated_farmer.get_products(
                db_storage.get_session())
            return render_template('dashboard.html',
                                   name=user_session['user_name'],
                                   email=user_session['user_email'],
                                   authenticated=user_session['authenticated'],
                                   products=products)
        else:
            flash('Authenticated farmer not found', 'error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/view_cart', methods=['GET', 'POST'])
def view_cart():
    try:
        # Check if the user is logged in
        if 'user_id' not in user_session:
            flash('You need to be logged in to view your cart', 'error')
            return redirect(url_for('login'))

        # Get the authenticated consumer
        authenticated_consumer = (db_storage.get_session().query(Consumer).
                                  filter_by(id=user_session['user_id']).first())

        # Check if the authenticated consumer exists
        if not authenticated_consumer:
            flash('Authenticated consumer not found', 'error')
            return redirect(url_for('login'))

        # Handle form submissions for editing quantities
        if request.method == 'POST':
            product_id = request.form['product_id']
            new_quantity = int(request.form['new_quantity'])

            # Use the edit_quantity method from the Cart class
            if Cart.edit_quantity(db_storage.get_session(), product_id,
                                  authenticated_consumer.id, new_quantity):
                flash('Quantity updated successfully', 'success')
            else:
                flash('Error updating quantity', 'error')

            return redirect(url_for('view_cart'))

        # Get the cart items for the authenticated consumer
        cart_items = (
            db_storage.get_session()
            .query(Cart, Product)
            .join(Product, Cart.product_id == Product.id)
            .filter(Cart.consumer_id == authenticated_consumer.id)
            .all()
        )

        # Calculate the total quantity and total cost of items in the cart
        total_quantity = sum(cart_item.quantity for cart_item, _ in cart_items)
        total_cost = sum(cart_item.quantity * product.price for cart_item, product in cart_items)

        return render_template('cart.html',
                               cart_items=cart_items,
                               total_quantity=total_quantity,
                               total_cost=total_cost)

    except SQLAlchemyError as e:
        flash(f"Error viewing cart: {e}", 'error')

    return redirect(url_for('index'))


@app.route('/delete_item/<item_id>')
def delete_item(item_id):
    try:
        # Check if the user is logged in
        if 'user_id' not in user_session:
            flash('You need to be logged in to delete items from your cart', 'error')
            return redirect(url_for('login'))

        # Get the authenticated consumer
        authenticated_consumer = (db_storage.get_session().query(Consumer).
                                  filter_by(id=user_session['user_id']).first())

        # Check if the authenticated consumer exists
        if not authenticated_consumer:
            flash('Authenticated consumer not found', 'error')
            return redirect(url_for('login'))

        # Use the delete_item method from the Cart class
        if Cart.delete_item(db_storage.get_session(), item_id,
                            authenticated_consumer.id):
            flash('Item deleted successfully', 'success')
        else:
            flash('Error deleting item', 'error')

        return redirect(url_for('view_cart'))

    except SQLAlchemyError as e:
        flash(f"Error deleting item: {e}", 'error')

    return redirect(url_for('view_products'))


@app.route('/add_product', methods=['POST'])
def add_new_product():
    u_id = str(uuid.uuid4())
    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    location = request.form['location']
    quantity = request.form['quantity']
    farmer_id = user_session['user_id']
    created_at = datetime.now()
    updated_at = datetime.now()

    # Create a session to interact with the database
    session = db_storage.get_session()

    Product.add_product(session, u_id, name, category, price,
                        location, quantity, farmer_id, created_at, updated_at)
    return redirect(url_for('dashboard'))


@app.route('/update_product/<product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    try:
        # Check if the user is logged in
        if 'user_id' not in user_session:
            flash('You need to be logged in to update a product', 'error')
            return redirect(url_for('login'))

        # Get the authenticated farmer
        authenticated_farmer = db_storage.get_session().query(Farmer).filter_by(id=user_session['user_id']).first()

        # Check if the authenticated farmer exists
        if not authenticated_farmer:
            flash('Authenticated farmer not found', 'error')
            return redirect(url_for('login'))

        # Get the product to update
        product_to_update = (
            db_storage.get_session()
            .query(Product)
            .filter_by(id=product_id, farmer_id=authenticated_farmer.id)
            .first()
        )

        # Check if the product belongs to the authenticated farmer
        if not product_to_update:
            flash('Product not found or does not belong to the authenticated '
                  'farmer', 'error')
            return redirect(url_for('dashboard'))

        # Handle form submission for updating the product
        if request.method == 'POST':
            new_data = {
                'name': request.form['name'],
                'category': request.form['category'],
                'price': float(request.form['price']),
                'location': request.form['location'],
                'quantity': int(request.form['quantity']),
            }

            # Attempt to update the product
            if Product.update_product(db_storage.get_session(), product_id,
                                      authenticated_farmer.id, new_data):
                flash('Product updated successfully', 'success')
            else:
                flash('Error updating product', 'error')

            return redirect(url_for('dashboard'))

        return redirect(url_for('dashboard'))

    except SQLAlchemyError as e:
        flash(f"Error updating product: {e}", 'error')

    return redirect(url_for('dashboard'))


@app.route('/delete_product/<product_id>', methods=['POST', 'GET'])
def delete_product(product_id):
    try:
        # Check if the user is logged in
        if 'user_id' not in user_session:
            flash('You need to be logged in to delete a product', 'error')
            return redirect(url_for('login'))

        # Get the authenticated farmer
        authenticated_farmer = (db_storage.get_session().query(Farmer)
                                .filter_by(id=user_session['user_id']).first())

        # Check if the authenticated farmer exists
        if not authenticated_farmer:
            flash('Authenticated farmer not found', 'error')
            return redirect(url_for('login'))

        # Attempt to delete the product
        result = Product.delete_product(db_storage.get_session(),
                                        product_id=product_id,
                                        farmer_id=authenticated_farmer.id
                                        )
        if result:
            flash('Product deleted successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Product not found or does not belong to the authenticated '
                  'farmer', 'error')
            return redirect(url_for('dashboard'))

    except SQLAlchemyError as e:
        flash(f"Error deleting product: {e}", 'error')

    return redirect(url_for('farmer_dashboard'))


@app.route('/add_item', methods=['POST'])
def add_item_to_cart():
    try:
        # Check if the user is logged in
        if 'user_id' not in user_session:
            flash('You need to be logged in to add items to the cart', 'error')
            return redirect(url_for('login'))

        # Get the authenticated consumer
        authenticated_consumer = (db_storage.get_session().query(Consumer)
                                  .filter_by(id=user_session['user_id'])
                                  .first())

        # Check if the authenticated consumer exists
        if not authenticated_consumer:
            flash('Authenticated consumer not found', 'error')
            return redirect(url_for('login'))

        # Get the form data
        id = str(uuid.uuid4())
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        consumer_id = request.form['consumer_id']
        created_at = datetime.now()
        updated_at = datetime.now()

        # Use the add_item method from the Cart class
        if Cart.add_item(db_storage.get_session(), u_id=id,
                         product_id=product_id,
                         consumer_id=consumer_id,
                         quantity=quantity,
                         created_at=created_at,
                         updated_at=updated_at):
            flash('Item added to cart successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error adding item to cart', 'error')

        return redirect(url_for('index'))

    except SQLAlchemyError as e:
        flash(f"Error adding item to cart: {e}", 'error')

    return redirect(url_for('index'))


@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        # Check if the user is logged in
        if 'user_id' not in user_session:
            flash('You need to be logged in to place an order', 'error')
            return redirect(url_for('login'))

        # Get the authenticated consumer
        authenticated_consumer = (db_storage.get_session().query(Consumer).
                                  filter_by(id=user_session['user_id']).first())

        # Check if the authenticated consumer exists
        if not authenticated_consumer:
            flash('Authenticated consumer not found', 'error')
            return redirect(url_for('login'))

        # Use the place_order method from the Order class
        id = str(uuid.uuid4())
        if Order.place_order(db_storage.get_session(), id,
                             authenticated_consumer.id,
                             authenticated_consumer.location):
            flash('Order placed successfully', 'success')
        else:
            flash('Error placing order', 'error')

        return redirect(url_for('index'))

    except SQLAlchemyError as e:
        flash(f"Error placing order: {e}", 'error')

    return redirect(url_for('index'))

def authenticate_farmer(email, password):
    # Create a session to interact with the database
    session = db_storage.get_session()
    try:
        # Query the database for the provided email
        farmer = session.query(Farmer).filter_by(email=email).first()

        # Check if the farmer exists and the password matches
        if farmer and farmer.password == password:
            return farmer
    except SQLAlchemyError as e:
        print(f"Error authenticating farmer: {e}")
    finally:
        # Close the session
        session.close()
    # print("Not found in farmer")
    return None


def authenticate_consumer(email, password):
    # Create a session to interact with the database
    session = db_storage.get_session()
    try:
        # Query the database for the provided email
        consumer = session.query(Consumer).filter_by(email=email).first()

        # Check if the farmer exists and the password matches
        if consumer and consumer.password == password:
            return consumer
    except SQLAlchemyError as e:
        print(f"Error authenticating consumer: {e}")
    finally:
        # Close the session
        session.close()
    # print("Not found in farmer")
    return None


if __name__ == '__main__':
    app.run(debug=True)
