from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..models.models import User
from ..extensions import db
from ..utils.permit_helper import create_permit_user, assign_role

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login", methods=["GET", "POST"])
async def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        flash("Please check your login details and try again.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth.route("/register", methods=["GET", "POST"])
async def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists.", "danger")
            return redirect(url_for("auth.register"))

        # Create user in database
        try:
            user = User(email=email, username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Sync with Permit.io
            try:
                await create_permit_user(user)
                await assign_role(str(user.id), "viewer")

                flash("Registration successful!", "success")
                return redirect(url_for("auth.login"))

            except Exception as e:
                # If permit sync fails, rollback user creation
                db.session.delete(user)
                db.session.commit()
                flash(
                    "Error syncing with authorization service. Please try again.",
                    "danger",
                )
                print(f"Permit.io sync error: {str(e)}")
                return redirect(url_for("auth.register"))

        except Exception as e:
            flash("Error during registration. Please try again.", "danger")
            print(f"Registration error: {str(e)}")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html")


@auth.route("/logout")
@login_required
async def logout():
    logout_user()
    return redirect(url_for("main.index"))
