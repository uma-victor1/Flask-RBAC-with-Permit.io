from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure LoginManager
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register blueprints
    from .routes.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from .routes.tasks import tasks as tasks_blueprint

    app.register_blueprint(tasks_blueprint)

    return app
