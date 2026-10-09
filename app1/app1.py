import os
import sys

# Ensure current directory is in sys.path so models can be imported from anywhere
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

try:
    from models import db, User, Specialty
except ImportError:
    from app1.models import db, User, Specialty

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'health_portal.db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def seed_initial_data():
    """Creates tables and seeds default specialties and admin user."""
    db.create_all()

    # Seed default specialties
    specialties = ["Cardiology", "Dermatology", "Pediatrics", "Orthopedics", "General Medicine"]
    for spec_name in specialties:
        if not Specialty.query.filter_by(name=spec_name).first():
            db.session.add(Specialty(name=spec_name))

    # Seed or reset admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            mobile_no='9876543210',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("Created default admin user: username='admin', password='admin123', mobile='9876543210'")
    else:
        if not admin.check_password('admin123'):
            admin.set_password('admin123')
            print("Updated admin password to 'admin123'")

    db.session.commit()


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Allow logging in via username OR mobile number
        user = User.query.filter(
            (User.username == identifier) | (User.mobile_no == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            
            # Redirect to next page if requested, else dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username/mobile number or password.', 'error')

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return f"""
    <h2>Dashboard</h2>
    <p>Welcome, <b>{current_user.username}</b>!</p>
    <p>Mobile: {current_user.mobile_no}</p>
    <p>Role: <span style="text-transform: capitalize;">{current_user.role}</span></p>
    <a href="{url_for('logout')}">Logout</a>
    """


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# Helper CLI command
@app.cli.command("init-db")
def init_db():
    """Creates database tables and seeds a sample admin and doctor."""
    with app.app_context():
        seed_initial_data()
        print("Database initialized successfully!")


if __name__ == '__main__':
    with app.app_context():
        seed_initial_data()
    app.run(debug=True)