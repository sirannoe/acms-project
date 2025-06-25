# app/routes/main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")                       # 127.0.0.1:5000 lands here
def home():
    """
    ▸ If the user is already logged-in, go straight to the dashboard  
    ▸ Otherwise show the one-page Welcome + Login screen (login.html)
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_view"))
    return render_template("login.html")  # your combined welcome-login template
