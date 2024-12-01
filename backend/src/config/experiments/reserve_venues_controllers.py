from flask import request, jsonify
from slugify import slugify

from backend.src.models.city import City
from backend.src.models.venue import Venue
from backend.src.services.geonames_service import validate_and_get_names
from backend.src.services.here_service import validate_and_get_addr_and_location
from backend.src.utils.exceptions import UserError
from backend.src.utils.language_utils import validate_language
from backend.src.utils.constants import ALLOWED_VENUE_BODY_PARAMS, REQUIRED_VENUE_BODY_PARAMS, \
    OPTIONAL_VENUE_BODY_PARAMS
from werkzeug.exceptions import BadRequest


def get_all_venues():
    """
    Get list of all venues

    Query Parameters:
        - lang (str, optional): Language for venues (en, ru, he). Defaults to 'en'

    Returns:
        JSON response with:
        - status: success/error
        - data: list of venues or error message
        - count: total number of cities (only if successful)
    """
    if request.data:
        raise UserError("Using body in GET-method is restricted.")

    # Get language preference from query parameter, default to English
    lang_arg = request.args.get("lang", "en")
    language = validate_language(lang_arg)
    if language is None:
        raise UserError(f"Unsupported language: {lang_arg}")

    # Get active preferences for venues
    is_active_arg = request.args.get("is_active")

    # Get all venues from database
    match is_active_arg:
        case "true":
            venues = Venue.objects(is_active=True)
        case "false":
            venues = Venue.objects(is_active=False)
        case None:
            venues = Venue.objects()
        case _:
            return jsonify({
                "status": "error",
                "message": "Parameter 'is_active' must be true or false"
            }), 400

    # Format response data using the requested language
    venues_data = [{
        "name": venue.get_name(language),
        "address": venue.get_address(language),
        "description": venue.get_description(language),
        "city": {
            "name": venue.city.get_name(language),
            "slug": venue.city.slug
        },
        "location": venue.location,
        "website": venue.website,
        "phone": venue.phone,
        "email": venue.email,
        "is_active": venue.is_active,
        "slug": venue.slug
    } for venue in venues]

    return jsonify({
        'status': 'success',
        'data': venues_data,
        'count': len(venues_data)
    }), 200


def create_new_venue():
    """
    Create new venue

    Query Body Parameters:
        - name_en (str, required): Name in English
        - name_ru (str, required): Name in Russian
        - name_he (str, required): Name in Hebrew
        - address_en (str, required): Address in English
        - description_en (str, required): Description in English
        - description_ru (str, required): Description in Russian
        - description_he (str, required): Description in Hebrew
        - city_en (str, required): City name in English
        - website (str, optional): website of the venue (URL)
        - phone (str, optional): phone number of the venue
        - email (str, optional): email of the venue
        - image_path (str, optional): image of the venue

    Returns:
        JSON response with:
        - status: success/error
        - message: new venue created
    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    unknown_params = set(data.keys()) - ALLOWED_VENUE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    if 12 < len(data) < 8:
        raise UserError("Incorrect number of parameters in body.")

    for param in REQUIRED_VENUE_BODY_PARAMS:
        if param not in data:
            raise UserError(f"Body parameter '{param}' is missing.")
        elif not isinstance(data[param], str):
            raise UserError(f"Body parameter {param} must be a string.")

    for param in OPTIONAL_VENUE_BODY_PARAMS:
        if param in data and not isinstance(data["website"], str):
            raise UserError(f"Body parameter {param} must be a string.")

    # Check if city exists, if not - try to add it
    city = City.objects(name_en=data["city_en"]).first()

    # If city doesn't exist, add it using GeoNames
    if not city:
        names = validate_and_get_names(data["city_en"])
        city = City(
            name_en=names["en"],
            name_ru=names["ru"],
            name_he=names["he"],
            slug=slugify(names["en"])
        )
        city.save()

    # Get address translations and coordinates from HERE API
    full_address_en = f"{data['address_en']}, {city.name_en}"
    address_data = validate_and_get_addr_and_location(full_address_en)

    venue = Venue(
        name_en=data["name_en"],
        name_ru=data["name_ru"],
        name_he=data["name_he"],
        address_en=address_data["en"],
        address_ru=address_data["ru"],
        address_he=address_data["he"],
        description_en=data["description_en"],
        description_ru=data["description_ru"],
        description_he=data["description_he"],
        city=city,
        location=address_data["location"],
        phone=data.get("phone"),
        website=data.get("website"),
        slug=slugify(data["name_en"])
    )

    venue.save()

    return jsonify({
        'status': 'success',
        'message': 'Venue created successfully'
    }), 201
