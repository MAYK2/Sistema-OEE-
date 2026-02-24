from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            error = "Usuario o contraseña incorrectos"
            
    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
