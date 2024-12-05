from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.controllers.events_controllers import get_all_events, get_existing_event, create_new_event
from backend.src.utils.custom_decorators import no_body_in_request, manager_required, no_args_in_request

# Create Blueprint for events
events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.route("/", methods=["GET"])
@no_body_in_request()
def get_events():
    return get_all_events()


@events_bp.route("/<slug>", methods=["GET"])
@no_body_in_request()
def get_event(slug):
    return get_existing_event(slug)


@events_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@no_args_in_request()
def create_event():
    return create_new_event()


# @venues_bp.route("/<slug>", methods=["PUT"])
# @jwt_required()
# @manager_required()
# @no_args_in_request()
# def full_update_venue(slug):
#     return full_update_existing_venue(slug)
#
#
# @venues_bp.route("/<slug>", methods=["PATCH"])
# @jwt_required()
# @manager_required()
# @no_args_in_request()
# def part_update_venue(slug):
#     return part_update_existing_venue(slug)
#
#
# @venues_bp.route("/<slug>", methods=["DELETE"])
# @jwt_required()
# @manager_required()
# @no_body_in_request()
# @no_args_in_request()
# def delete_venue(slug):
#     """Handle DELETE request for deleting one venue"""
#     return delete_existing_venue(slug)
