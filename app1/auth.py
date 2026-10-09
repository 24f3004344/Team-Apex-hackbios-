from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard')) # Change to your dashboard route
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')