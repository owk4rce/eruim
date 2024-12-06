from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import public_routes_limit, protected_routes_limit
from backend.src.controllers.event_types_controller import get_all_event_types, create_new_event_type, \
    full_update_existing_event_type, part_update_existing_event_type, delete_existing_event_type, \
    get_existing_event_type
from backend.src.utils.custom_decorators import no_body_in_request, require_json, manager_required, no_args_in_request

# Create Blueprint for event types
event_types_bp = Blueprint("event_types", __name__, url_prefix="/event_types")


@event_types_bp.route("/", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_event_types():
    """Handle GET request for retrieving all event types"""
    return get_all_event_types()


@event_types_bp.route("/<slug>", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_event_type(slug):
    """Handle GET request for retrieving one venue type"""
    return get_existing_event_type(slug)


@event_types_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def create_event_type():
    """Handle POST request for creating new event type"""
    return create_new_event_type()


@event_types_bp.route("/<slug>", methods=["PUT"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def full_update_event_type(slug):
    """Handle PUT request for full updating one event type"""
    return full_update_existing_event_type(slug)


@event_types_bp.route("/<slug>", methods=["PATCH"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def part_update_event_type(slug):
    """Handle PATCH request for partial updating one event type"""
    return part_update_existing_event_type(slug)


@event_types_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def delete_event_type(slug):
    """Handle DELETE request for deleting one event type"""
    return delete_existing_event_type(slug)
