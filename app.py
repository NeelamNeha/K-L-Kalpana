from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# Configuration for Database URI and secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:t1a2j3m4@localhost/internship_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # Random secret key for sessions

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    internships = db.relationship('Internship', backref='student', lazy=True)

class Internship(db.Model):
    __tablename__ = 'internships'
    
    internship_id = db.Column(db.Integer, primary_key=True)  # No auto increment here
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    external_mentor_name = db.Column(db.String(255), nullable=False)
    external_mentor_contact = db.Column(db.String(255), nullable=False)
    external_mentor_email = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    company_address = db.Column(db.Text, nullable=False)
    company_registration_number = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    stipend_amount = db.Column(db.Numeric(10, 2), nullable=False)
    offer_letter_url = db.Column(db.String(2048), nullable=False)

    student = db.relationship('User', backref='internships', lazy=True)


    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get data from the form
        user_id = request.form['user_id']  # Get user_id input from the form
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        phone_number = request.form['phone_number']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please choose a different one.', 'danger')
        else:
            # Create a new User record with user_id
            new_user = User(user_id=user_id,  # Use the user_id provided in the form
                            name=name, 
                            email=email, 
                            role=role, 
                            phone_number=phone_number, 
                            password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user exists in the database
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['name'] = user.name
            session['role'] = user.role
            session['email'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    internships = Internship.query.all()
    return render_template('dashboard.html', internships=internships)
@app.route('/add_internship', methods=['GET', 'POST'])
def add_internship():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Capture internship details from the form
            internship_id = request.form['internship_id']
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            company_name = request.form['company_name']
            company_address = request.form['company_address']
            external_mentor_name = request.form['external_mentor_name']
            external_mentor_contact = request.form['external_mentor_contact']
            external_mentor_email = request.form['external_mentor_email']
            company_reg_number = request.form['company_registration_number']
            city = request.form['city']
            stipend_amount = float(request.form['stipend_amount'])
            offer_letter_url = request.form['offer_letter_url']

            # Create a new Internship record with user-provided internship_id
            new_internship = Internship(
                internship_id=int(internship_id),  # Manually setting internship_id
                student_id=session['user_id'],  # Associate with logged-in user
                start_date=start_date,
                company_name=company_name,
                company_address=company_address,
                external_mentor_name=external_mentor_name,
                external_mentor_contact=external_mentor_contact,
                external_mentor_email=external_mentor_email,
                company_registration_number=company_reg_number,
                city=city,
                stipend_amount=stipend_amount,
                offer_letter_url=offer_letter_url
            )

            # Add and commit the internship record
            db.session.add(new_internship)
            db.session.commit()

            flash('Internship details added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred: {e}', 'danger')

    return render_template('add_internship.html')

# Logout Route
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))  # Redirect to login page

if __name__ == '__main__':
    app.run(debug=True)
