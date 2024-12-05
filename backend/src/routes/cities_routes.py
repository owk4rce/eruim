from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.controllers.cities_controller import get_all_cities, create_new_city, delete_existing_city, \
    get_existing_city
from backend.src.utils.custom_decorators import no_body_in_request, manager_required, require_json, no_args_in_request, \
    admin_required

# Create Blueprint for cities
cities_bp = Blueprint("cities", __name__, url_prefix="/cities")


@cities_bp.route("/", methods=["GET"])
@no_body_in_request()
def get_cities():
    return get_all_cities()


@cities_bp.route("/<slug>", methods=["GET"])
@no_body_in_request()
def get_city(slug):
    """Handle GET request for retrieving one city"""
    return get_existing_city(slug)


@cities_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@require_json()
@no_args_in_request()
def create_city():
    return create_new_city()


@cities_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@admin_required()
@no_body_in_request()
@no_args_in_request()
def delete_city(slug):
    """Handle DELETE request for deleting one city"""
    return delete_existing_city(slug)
