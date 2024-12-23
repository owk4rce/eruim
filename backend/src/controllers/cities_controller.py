from flask import request, jsonify
from slugify import slugify

from backend.src.models.venue import Venue
from backend.src.services.geonames_service import validate_and_get_names
from backend.src.utils.constants import SUPPORTED_LANGUAGES
from backend.src.utils.exceptions import UserError
from backend.src.models.city import City
from backend.src.utils.pre_mongo_validators import validate_city_data

import logging

logger = logging.getLogger("backend")


def get_all_cities():
    """
    Get list of all cities.

    Query params:
        lang (optional): Response language (en/ru/he)

    Returns:
        Cities list in requested language
    """
    unknown_args = set(request.args.keys()) - {"lang"}
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    # Get language preference from query parameter
    lang_arg = request.args.get("lang")
    if lang_arg:
        if lang_arg not in SUPPORTED_LANGUAGES:
            raise UserError(f"Unsupported language: {lang_arg}")

    # Get all cities from database
    cities = City.objects()
    # Format response data using the requested language
    cities_data = [city.to_response_dict(lang_arg) for city in cities]

    return jsonify({
        "status": "success",
        "data": cities_data,
        "count": City.objects.count()
    }), 200


def get_existing_city(slug):
    """
    Get single city by slug.

    Query params:
        lang (optional): Response language (en/ru/he)

    Returns:
        City data in requested language
    """
    unknown_args = set(request.args.keys()) - {"lang"}
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    # Get language preference from query parameter
    lang_arg = request.args.get("lang")
    if lang_arg:
        if lang_arg not in SUPPORTED_LANGUAGES:
            raise UserError(f"Unsupported language: {lang_arg}")

    # Get one venue type from database
    city = City.objects(slug=slug).first()

    if not city:
        raise UserError(f"City with slug {slug} not found", 404)

    # Format response data using the requested language
    city_data = city.to_response_dict(lang_arg)

    return jsonify({
        "status": "success",
        "data": city_data
    }), 200


def create_new_city():
    """
    Create new city using GeoNames validation.

    Expected body:
        {
            "name_en": "Jerusalem"  # English name only
        }

    Process:
        1. Validates English name
        2. Gets translations from GeoNames
        3. Creates city with all names
    """
    data = request.get_json()

    if len(data) != 1 or "name_en" not in data:
        raise UserError("Body of request must contain only 'name_en' parameter.")

    validate_city_data(data)

    # Check if city already exists
    if City.objects(name_en=data["name_en"]).first():
        raise UserError(f"City with name {data['name_en']} already exists", 409)

    names = validate_and_get_names(data['name_en'])  # geovalidation and getting names

    city = City(name_en=names["en"],
                name_ru=names["ru"],
                name_he=names["he"],
                slug=slugify(names['en'])
                )
    city.save()

    logger.info(f"Created new city: {names['en']}")

    return jsonify({
        "status": "success",
        "message": "City created successfully",
        "data": city.to_response_dict()
    }), 201


def delete_existing_city(slug):
    """
    Delete city if no associated venues exist.
    """
    # Find existing city
    city = City.objects(slug=slug).first()
    if not city:
        raise UserError(f"City with slug '{slug}' not found", 404)

    associated_venues = Venue.objects(city=city).count()

    if associated_venues > 0:
        raise UserError(
            "Cannot delete this city. Please delete all associated venues first.",
            409
        )

    logger.info(f"Deleting city: {city.name_en}")

    # If no associated venues, delete the city
    city.delete()

    # Return 204 No Content for successful deletion
    return '', 204
