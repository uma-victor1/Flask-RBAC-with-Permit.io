from flask.cli import FlaskGroup
from app.main import create_app
from app.extensions import db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

cli = FlaskGroup(app)


@cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Database initialized!")


if __name__ == "__main__":
    app.run(debug=True)
