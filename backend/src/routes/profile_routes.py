from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.controllers.profile_controller import get_user_profile, full_update_user_profile, \
    part_update_user_profile, add_event_to_favorites, remove_event_from_favorites

from backend.src.utils.custom_decorators import no_body_in_request, no_args_in_request, require_json, \
    check_active_user

# Create Blueprint for venue types
profile_bp = Blueprint("profile", __name__, url_prefix="/users/me")


@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
@check_active_user()
@no_body_in_request()
@no_args_in_request()
def get_profile():
    """ """
    return get_user_profile()


@profile_bp.route("/profile", methods=["PUT"])
@jwt_required()
@check_active_user()
@require_json()
@no_args_in_request()
def full_update_profile():
    """ """
    return full_update_user_profile()


@profile_bp.route("/profile", methods=["PATCH"])
@jwt_required()
@check_active_user()
@require_json()
@no_args_in_request()
def part_update_profile():
    """ """
    return part_update_user_profile()


@profile_bp.route("/profile/fav/<event_slug>", methods=["POST"])
@jwt_required()
@check_active_user()
@no_body_in_request()
@no_args_in_request()
def add_to_favorites(event_slug):
    """ """
    return add_event_to_favorites(event_slug)


@profile_bp.route("/profile/fav/<event_slug>", methods=["DELETE"])
@jwt_required()
@check_active_user()
@no_body_in_request()
@no_args_in_request()
def remove_from_favorites(event_slug):
    """Handle DELETE request for deleting one user"""
    return remove_event_from_favorites(event_slug)
