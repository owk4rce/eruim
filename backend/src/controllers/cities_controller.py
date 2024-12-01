from flask import request, jsonify
from slugify import slugify

from backend.src.models.venue import Venue
from backend.src.services.geonames_service import validate_and_get_names
from backend.src.utils.exceptions import UserError
from backend.src.utils.language_utils import validate_language
from backend.src.models.city import City
from backend.src.utils.pre_mongo_validators import validate_city_data


def get_all_cities():
    """
    Get list of all cities

    Query Parameters:
        - lang (str, optional): Language for city names (en, ru, he). Defaults to 'en'

    Returns:
        JSON response with:
        - status: success/error
        - data: list of cities or error message
        - count: total number of cities (only if successful)
    """
    if request.data:
        raise UserError("Using body in GET-method is restricted.")

    # Get language preference from query parameter, default to English
    lang_arg = request.args.get("lang", "en")
    language = validate_language(lang_arg)
    if language is None:
        raise UserError(f"Unsupported language: {lang_arg}")

    # Get all cities from database
    cities = City.objects()
    # Format response data using the requested language
    cities_data = [city.to_response_dict(language) for city in cities]

    return jsonify({
        "status": "success",
        "data": cities_data,
        "count": len(cities_data)
    }), 200


def create_new_city():
    """
    Create new city

    Query Body Parameters:
        - name_en (str, required): Name in English

    Returns:
        JSON response with:
        - status: success/error
        - message: new city created
    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    if len(data) != 1 or "name_en" not in data:
        raise UserError("Body of request must contain only 'name_en' field.")

    validate_city_data(data)

    names = validate_and_get_names(data['name_en'])     # geovalidation and getting names

    city = City(name_en=names["en"],
                name_ru=names["ru"],
                name_he=names["he"],
                slug=slugify(names['en'])
                )
    city.save()

    return jsonify({
        'status': 'success',
        'message': 'City created successfully',
        "data": city.to_response_dict()
    }), 201


def delete_existing_city(slug):
    """
    Delete existing city if there are no venues

    Returns:
        JSON response with:
        - status: error
        - message: event type updated

        204
    """
    if request.data:
        raise UserError("Using body in DELETE-method is restricted.")

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

    # If no associated venues, delete the city
    city.delete()

    # Return 204 No Content for successful deletion
    return '', 204
