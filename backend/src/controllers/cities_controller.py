from flask import request, jsonify
from slugify import slugify
from backend.src.services.geonames_service import validate_and_get_names
from backend.src.utils.exceptions import UserError
from backend.src.utils.language_utils import validate_language
from backend.src.models.city import City


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
    cities_data = [{
        "name": city.get_name(language),
        "slug": city.slug
    } for city in cities]

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

    names = validate_and_get_names(data['name_en'])

    city = City(name_en=names["en"],
                name_ru=names["ru"],
                name_he=names["he"],
                slug=slugify(names['en'])
                )
    city.save()

    return jsonify({
        'status': 'success',
        'message': 'City created successfully'
    }), 201
