from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import public_routes_limit, protected_routes_limit
from backend.src.controllers.venues_controllers import get_all_venues, create_new_venue, get_existing_venue, \
    full_update_existing_venue, part_update_existing_venue, delete_existing_venue
from backend.src.utils.custom_decorators import no_body_in_request, manager_required, no_args_in_request

# Create Blueprint for venues
venues_bp = Blueprint("venues", __name__, url_prefix="/venues")


@venues_bp.route("/", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_venues():
    return get_all_venues()


@venues_bp.route("/<slug>", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_venue(slug):
    return get_existing_venue(slug)


@venues_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def create_venue():
    return create_new_venue()


@venues_bp.route("/<slug>", methods=["PUT"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def full_update_venue(slug):
    return full_update_existing_venue(slug)


@venues_bp.route("/<slug>", methods=["PATCH"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def part_update_venue(slug):
    return part_update_existing_venue(slug)


@venues_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def delete_venue(slug):
    """Handle DELETE request for deleting one venue"""
    return delete_existing_venue(slug)
