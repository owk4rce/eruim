from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import auth_limit, public_routes_limit
from backend.src.controllers.auth_controllers import register_new_user, existing_user_login, user_logout, \
    request_password_reset, verify_reset_token, confirm_password_reset
from backend.src.utils.custom_decorators import require_json, no_args_in_request, no_body_in_request

# Create Blueprint for authorization
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
@public_routes_limit()
@require_json()
@no_args_in_request()
def register_user():
    """Handle POST request for registration"""
    return register_new_user()


@auth_bp.route("/login", methods=["POST"])
@auth_limit()
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


@auth_bp.route("/reset-password/request", methods=["POST"])
@auth_limit()
@require_json()
@no_args_in_request()
def request_pwd_reset():
    """Handle POST request for registration"""
    return request_password_reset()


@auth_bp.route("/reset-password/verify", methods=["GET"])
@auth_limit()
@no_body_in_request()
def verify_token():
    """Handle GET request for token verification"""
    return verify_reset_token()


@auth_bp.route("/reset-password/confirm", methods=["POST"])
@auth_limit()
@require_json()
@no_args_in_request()
def reset_password_confirm():
    """Handle POST request for setting new password"""
    return confirm_password_reset()