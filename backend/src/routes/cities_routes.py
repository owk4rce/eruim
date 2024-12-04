from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.controllers.cities_controller import get_all_cities, create_new_city, delete_existing_city, \
    get_existing_city

# Create Blueprint for cities
cities_bp = Blueprint("cities", __name__, url_prefix="/cities")


@cities_bp.route("/", methods=["GET"])
def get_cities():
    return get_all_cities()


@cities_bp.route("/<slug>", methods=["GET"])
def get_city(slug):
    """Handle GET request for retrieving one city"""
    return get_existing_city(slug)


@cities_bp.route("/", methods=["POST"])
@jwt_required()
def create_city():
    return create_new_city()


@cities_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
def delete_city(slug):
    """Handle DELETE request for deleting one city"""
    return delete_existing_city(slug)
