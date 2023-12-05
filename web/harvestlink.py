import uuid

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as user_session
from sqlalchemy.exc import SQLAlchemyError

from models.farmers import add_farmer, Farmer
from models.consumers import add_consumer, Consumer
from models.engine.storage import DatabaseStorage

app = Flask(__name__)
app.secret_key = 'hl_user_session'

# Initialize the DatabaseStorage
db_storage = DatabaseStorage()


@app.route('/')
def index():
    if 'user_id' in user_session:
        return render_template('index.html',
                               name=user_session['user_name'],
                               email=user_session['user_email'],
                               authenticated=user_session['authenticated'])
    return render_template('index.html')


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
        add_farmer(session, u_id=u_id, name=name, email=email, phone=phone,
                   location=location, password=password)
        return redirect(url_for('index'))
    elif acc == "consumer":
        # Add the consumer to the 'consumers' table
        add_consumer(session, u_id=u_id, name=name, email=email, phone=phone,
                     location=location, password=password)
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
        return render_template('dashboard.html',
                               name=user_session['user_name'],
                               email=user_session['user_email'])
    else:
        return redirect(url_for('login'))


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
