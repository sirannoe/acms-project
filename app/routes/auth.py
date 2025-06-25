# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app.models import db, User
from app.models import Role
from functools import wraps
from flask import abort

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role is None or current_user.role.name not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(request.args.get('next') or url_for('dashboard.dashboard_view'))
        flash("Invalid credentials","danger")
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
