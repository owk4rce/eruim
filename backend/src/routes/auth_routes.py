from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.controllers.auth_controllers import register_new_user, existing_user_login, user_logout

# Create Blueprint for authorization
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register_user():
    """Handle POST request for registration"""
    return register_new_user()


@auth_bp.route("/login", methods=["POST"])
def user_login():
    """Handle POST request for login"""
    return existing_user_login()


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Handle POST request for logout"""
    return user_logout()
