"""
LifeLens AI – Main Application Entry Point
Initializes Flask, SQLAlchemy, Flask-Login, and registers all blueprints.
"""

import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config.config import Config
from models import db
from models.user import User

login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please log in to access LifeLens AI.'

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.finance import finance_bp
    from routes.study import study_bp
    from routes.habits import habits_bp
    from routes.simulation import simulation_bp
    from routes.chatbot import chatbot_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(finance_bp, url_prefix='/finance')
    app.register_blueprint(study_bp, url_prefix='/study')
    app.register_blueprint(habits_bp, url_prefix='/habits')
    app.register_blueprint(simulation_bp, url_prefix='/simulation')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

    # Root redirect
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    # Create all database tables
    with app.app_context():
        db.create_all()
        # Seed sample data if DB is empty
        try:
            from database.seed import seed_if_empty
            seed_if_empty()
        except Exception as e:
            app.logger.warning(f"Seed skipped: {e}")

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
