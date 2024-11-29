from flask import Blueprint
from backend.src.controllers.venues_controllers import get_all_venues, create_new_venue


# Create Blueprint for venues
venues_bp = Blueprint("venues", __name__, url_prefix="/venues")


@venues_bp.route("/", methods=["GET"])
def get_venues():
    return get_all_venues()


@venues_bp.route("/", methods=["POST"])
def create_venue():
    return create_new_venue()

