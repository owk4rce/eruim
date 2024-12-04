from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.controllers.users_controller import get_all_users, get_existing_user, create_new_user, \
    full_update_existing_user, part_update_existing_user, delete_existing_user
from backend.src.utils.custom_decorators import admin_required, no_body_in_request, no_args_in_request, require_json

# Create Blueprint for venue types
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required()
@no_body_in_request()
def get_users():
    """Handle GET request for retrieving all users"""
    return get_all_users()


@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
@admin_required()
@no_body_in_request()
@no_args_in_request()
def get_user(user_id):
    """Handle GET request for retrieving one venue type"""
    return get_existing_user(user_id)


@users_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required()
@require_json()
@no_args_in_request()
def create_user():
    """Handle POST request for creating new user (only by admin)"""
    return create_new_user()


@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
@admin_required()
@require_json()
@no_args_in_request()
def full_update_user(user_id):
    """Handle PUT request for full updating one user"""
    return full_update_existing_user(user_id)


@users_bp.route("/<user_id>", methods=["PATCH"])
@jwt_required()
@admin_required()
@require_json()
@no_args_in_request()
def part_update_user(user_id):
    """Handle PATCH request for partial updating one user"""
    return part_update_existing_user(user_id)


@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@admin_required()
@no_body_in_request()
@no_args_in_request()
def delete_user(user_id):
    """Handle DELETE request for deleting one user"""
    return delete_existing_user(user_id)
