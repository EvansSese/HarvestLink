import uuid

from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

from models.farmers import add_farmer, Farmer
from models.engine.storage import DatabaseStorage

app = Flask(__name__)

# Initialize the DatabaseStorage
db_storage = DatabaseStorage()


@app.route('/')
def index():
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
    else:
        print('Consumer')

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def farmer_login():
    if request.method == 'POST':
        # Get the email and password from the form
        email = request.form.get('email')
        password = request.form.get('password')

        # Perform authentication
        farmer = authenticate_farmer(email, password)

        if farmer:
            return redirect(url_for('farmer_dashboard', name=farmer.name))
        else:
            return render_template('login.html', error_message="Incorrect credentials")

    return render_template('login.html')


@app.route('/farmer-dashboard/<name>')
def farmer_dashboard(name):
    return render_template('farmer-dashboard.html', farmer_name=name)


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
    return None


if __name__ == '__main__':
    app.run(debug=True)
