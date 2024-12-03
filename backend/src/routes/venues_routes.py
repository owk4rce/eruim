from flask import Blueprint
from backend.src.controllers.venues_controllers import get_all_venues, create_new_venue, get_existing_venue, \
    full_update_existing_venue, part_update_existing_venue, delete_existing_venue

# Create Blueprint for venues
venues_bp = Blueprint("venues", __name__, url_prefix="/venues")


@venues_bp.route("/", methods=["GET"])
def get_venues():
    return get_all_venues()


@venues_bp.route("/<slug>", methods=["GET"])
def get_venue(slug):
    return get_existing_venue(slug)


@venues_bp.route("/", methods=["POST"])
def create_venue():
    return create_new_venue()


@venues_bp.route("/<slug>", methods=["PUT"])
def full_update_venue(slug):
    return full_update_existing_venue(slug)


@venues_bp.route("/<slug>", methods=["PATCH"])
def part_update_venue(slug):
    return part_update_existing_venue(slug)


@venues_bp.route("/<slug>", methods=["DELETE"])
def delete_venue(slug):
    """Handle DELETE request for deleting one venue"""
    return delete_existing_venue(slug)
