from flask import Blueprint
from backend.src.controllers.cities_controller import get_all_cities, create_new_city


# Create Blueprint for cities
cities_bp = Blueprint("cities", __name__, url_prefix="/cities")


@cities_bp.route("/", methods=["GET"])
def get_cities():
    return get_all_cities()


@cities_bp.route("/", methods=["POST"])
def create_city():
    return create_new_city()

