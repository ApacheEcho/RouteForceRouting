"""
Authentication routes
"""

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import auth_bp
from app.models.database import db
from app.services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required", "error")
            return render_template("auth/login.html")

        try:
            # Get user from database
            db_service = DatabaseService()
            user = db_service.get_user_by_username(username)

            if user and user.check_password(password):
                # Login successful
                session["user_id"] = user.id
                session["username"] = user.username
                session["role"] = user.role

                # Update last login
                user.last_login = db.func.now()
                db.session.commit()

                flash(f"Welcome back, {user.username}!", "success")
                return redirect(url_for("main.index"))
            else:
                flash("Invalid username or password", "error")

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash("An error occurred during login", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        # Validation
        if not all([username, email, password, confirm_password]):
            flash("All fields are required", "error")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return render_template("auth/register.html")

        try:
            db_service = DatabaseService()

            # Check if username already exists
            if db_service.get_user_by_username(username):
                flash("Username already exists", "error")
                return render_template("auth/register.html")

            # Check if email already exists
            if db_service.get_user_by_email(email):
                flash("Email already exists", "error")
                return render_template("auth/register.html")

            # Create new user
            user = db_service.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            flash("An error occurred during registration", "error")

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    """User logout"""
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
def profile():
    """User profile page"""
    if "user_id" not in session:
        flash("Please log in to view your profile", "error")
        return redirect(url_for("auth.login"))

    try:
        db_service = DatabaseService()
        user = db_service.get_user_by_id(session["user_id"])

        if not user:
            flash("User not found", "error")
            return redirect(url_for("auth.login"))

        return render_template("auth/profile.html", user=user)

    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        flash("An error occurred loading your profile", "error")
        return redirect(url_for("main.index"))


@auth_bp.route("/api/current_user")
def api_current_user():
    """API endpoint to get current user info"""
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        db_service = DatabaseService()
        user = db_service.get_user_by_id(session["user_id"])

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "is_active": user.is_active,
            }
        )

    except Exception as e:
        logger.error(f"API current user error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
