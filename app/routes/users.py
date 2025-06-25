from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app.models import db, User, Role
from app.utils.forms import UserForm   # optional Flask-WTF form
from werkzeug.security import generate_password_hash

users_bp = Blueprint("users", __name__, url_prefix="/users")

def admin_required():
    if not (current_user.is_authenticated and current_user.has_role("Admin")):
        abort(403)

@users_bp.route("/")
@login_required
def list_users():
    admin_required()
    return render_template("users/list.html", users=User.query.all())

@users_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_user():
    admin_required()
    form = UserForm()
    if form.validate_on_submit():
        user          = User(username=form.username.data,
                             email=form.email.data)
        user.set_password(form.password.data)
        # attach role
        role = Role.query.filter_by(name=form.role.data).first()
        if role: user.roles.append(role)
        db.session.add(user); db.session.commit()
        flash("User created", "success")
        return redirect(url_for("users.list_users"))
    return render_template("users/form.html", form=form, action="Create")

@users_bp.route("/<int:uid>/edit", methods=["GET", "POST"])
@login_required
def edit_user(uid):
    admin_required()
    user = User.query.get_or_404(uid)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email    = form.email.data
        if form.password.data:
            user.set_password(form.password.data)
        user.roles = [Role.query.filter_by(name=form.role.data).first()]
        db.session.commit()
        flash("Updated.", "success")
        return redirect(url_for("users.list_users"))
    return render_template("users/form.html", form=form, action="Edit")

@users_bp.route("/<int:uid>/delete", methods=["POST"])
@login_required
def delete_user(uid):
    admin_required()
    user = User.query.get_or_404(uid)
    db.session.delete(user); db.session.commit()
    flash("Deleted.", "info")
    return redirect(url_for("users.list_users"))
