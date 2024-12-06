from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import auth_limit
from backend.src.controllers.auth_controllers import register_new_user, existing_user_login, user_logout
from backend.src.utils.custom_decorators import require_json, no_args_in_request, no_body_in_request

# Create Blueprint for authorization
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
@require_json()
@no_args_in_request()
def register_user():
    """Handle POST request for registration"""
    return register_new_user()


@auth_bp.route("/login", methods=["POST"])
#@auth_limit()
@require_json()
@no_args_in_request()
def user_login():
    """Handle POST request for login"""
    return existing_user_login()


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
@no_body_in_request()
@no_args_in_request()
def logout():
    """Handle POST request for logout"""
    return user_logout()
