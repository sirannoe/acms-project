# app/__init__.py

from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from datetime import datetime
from dotenv import load_dotenv

from app.extensions import db, migrate, bcrypt
from app.utils.utils import generate_key_stats

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # 🔐 Set up LoginManager
    login = LoginManager()
    login.init_app(app)
    login.login_view = 'auth.login'  # endpoint to redirect to
    login.login_message = 'Please log in to access this page.'

    from app.models import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # 📌 Custom 403 error handler (optional)
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    # Global context processors
    @app.context_processor
    def inject_now():
        return {'now': datetime.now}

    @app.context_processor
    def inject_key_stats():
        return dict(key_stats=generate_key_stats())


    # Import and register blueprints here
    from app.routes.main import main_bp
    from app.routes.patients import patients_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.appointments import appointments_bp
    from app.routes.sms_test import sms_test_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.whatsapp import whatsapp_bp
    from app.routes.reports import reports_bp
    from app.routes.admin_portal import admin_bp
    from app.routes.reminders import reminders_bp
    from app.cli.seed import seed

    app.register_blueprint(main_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(sms_test_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(whatsapp_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reminders_bp)
    app.cli.add_command(seed)

    return app
