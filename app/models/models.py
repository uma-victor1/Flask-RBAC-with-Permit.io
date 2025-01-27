from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased length for hash
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Tasks owned by the user
    owned_tasks = db.relationship(
        "Task", foreign_keys="Task.user_id", backref="owner", lazy=True
    )

    # Tasks assigned to the user
    assigned_tasks = db.relationship(
        "Task", foreign_keys="Task.assigned_to", backref="assignee", lazy=True
    )

    def set_password(self, password):
        """Hash password using pbkdf2 method instead of scrypt"""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending")
    priority = db.Column(db.String(20), default="medium")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # User who created/owns the task
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # User to whom the task is assigned
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"<Task {self.title}>"
