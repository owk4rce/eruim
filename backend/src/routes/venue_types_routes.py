from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.controllers.venue_types_controller import get_all_venue_types, create_new_venue_type, \
    full_update_existing_venue_type, part_update_existing_venue_type, delete_existing_venue_type, \
    get_existing_venue_type
from backend.src.utils.custom_decorators import no_body_in_request, manager_required, require_json, no_args_in_request

# Create Blueprint for venue types
venue_types_bp = Blueprint("venue_types", __name__, url_prefix="/venue_types")


@venue_types_bp.route("/", methods=["GET"])
@no_body_in_request()
def get_venue_types():
    """Handle GET request for retrieving all venue types"""
    return get_all_venue_types()


@venue_types_bp.route("/<slug>", methods=["GET"])
@no_body_in_request()
def get_venue_type(slug):
    """Handle GET request for retrieving one venue type"""
    return get_existing_venue_type(slug)


@venue_types_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@require_json()
@no_args_in_request()
def create_venue_type():
    """Handle POST request for creating new evenue type"""
    return create_new_venue_type()


@venue_types_bp.route("/<slug>", methods=["PUT"])
@jwt_required()
@manager_required()
@require_json()
@no_args_in_request()
def full_update_venue_type(slug):
    """Handle PUT request for full updating one venue type"""
    return full_update_existing_venue_type(slug)


@venue_types_bp.route("/<slug>", methods=["PATCH"])
@jwt_required()
@manager_required()
@require_json()
@no_args_in_request()
def part_update_venue_type(slug):
    """Handle PATCH request for partial updating one venue type"""
    return part_update_existing_venue_type(slug)


@venue_types_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@manager_required()
@no_body_in_request()
@no_args_in_request()
def delete_venue_type(slug):
    """Handle DELETE request for deleting one venue type"""
    return delete_existing_venue_type(slug)
