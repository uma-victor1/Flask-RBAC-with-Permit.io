from flask import Flask
from config import config
from . import extensions
from .cli import init_db_command


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    extensions.init_app(app)

    # Register CLI commands
    app.cli.add_command(init_db_command)

    # Register blueprints
    from .routes.main import main

    app.register_blueprint(main)

    from .routes.auth import auth

    app.register_blueprint(auth)

    from .routes.tasks import tasks

    app.register_blueprint(tasks)

    return app
