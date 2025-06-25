# app/routes/admin_portal.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import User, Role
from app.extensions import db
from flask_login import login_required, current_user

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def _admin_required():
    if not current_user.is_authenticated or not current_user.has_role("Admin"):
        abort(403)

@admin_bp.route("/users")
@login_required
def list_users():
    _admin_required()
    users = User.query.all()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    _admin_required()
    if request.method == "POST":
        username = request.form["username"].strip()
        email    = request.form["email"].strip()
        password = request.form["password"]
        role_name = request.form["role"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for("admin.create_user"))
        role = Role.query.filter_by(name=role_name).first()
        new_u = User(username=username, email=email)
        new_u.set_password(password)
        new_u.roles.append(role)
        db.session.add(new_u)
        db.session.commit()
        flash("User created", "success")
        return redirect(url_for("admin.list_users"))
    roles = Role.query.all()
    return render_template("admin/create_user.html", roles=roles)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/python run.pyedit_user.html', user=user)



@admin_bp.route("/users/delete/<int:uid>", methods=["POST"])
@login_required
def delete_user(uid):
    _admin_required()
    user = User.query.get_or_404(uid)
    if user.username == "admin":
        flash("Default admin cannot be deleted", "warning")
        return redirect(url_for("admin.list_users"))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted", "info")
    return redirect(url_for("admin.list_users"))
