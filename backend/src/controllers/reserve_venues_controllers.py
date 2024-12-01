from flask import request, jsonify
from slugify import slugify

from backend.src.models.city import City
from backend.src.models.venue import Venue
from backend.src.models.venue_type import VenueType
from backend.src.services.geonames_service import validate_and_get_names
from backend.src.services.here_service import validate_and_get_addr_and_location
from backend.src.services.translation_service import translate_with_google, translate_with_mymemory
from backend.src.utils.exceptions import UserError
from backend.src.utils.file_utils import validate_image, save_venue_image
from backend.src.utils.language_utils import validate_language
from backend.src.utils.constants import ALLOWED_VENUE_BODY_PARAMS, OPTIONAL_VENUE_BODY_PARAMS, \
    STRICTLY_REQUIRED_VENUE_BODY_PARAMS
from backend.src.utils.pre_mongo_validators import validate_venue_data


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

    # format response
    venues_data = [venue.to_response_dict(language) for venue in venues]

    return jsonify({
        "status": "success",
        "data": venues_data,
        "count": len(venues_data)
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
    file = None
    if request.content_type.startswith("multipart/form-data"):  # expecting file via form
        data = request.form.to_dict()
        if not data:
            raise UserError("Form data is empty")

        if "image" in request.files:
            file = request.files["image"]
            validate_image(file)
    elif not request.is_json:
        raise UserError("Content-Type must be either multipart/form-data or application/json", 415)
    else:
        data = request.get_json()
        if not data:
            raise UserError("JSON body is empty")

    unknown_params = set(data.keys()) - ALLOWED_VENUE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    for param in STRICTLY_REQUIRED_VENUE_BODY_PARAMS:
        if param not in data:
            raise UserError(f"Body parameter '{param}' is missing.")
        # elif not isinstance(data[param], str):
        #     raise UserError(f"Body parameter {param} must be a string.")

    # for param in OPTIONAL_VENUE_BODY_PARAMS:
    #     if param in data and not isinstance(data["website"], str):
    #         raise UserError(f"Body parameter {param} must be a string.")

    if 12 < len(data) < 5:
        raise UserError("Incorrect number of parameters in body.")

    validate_venue_data(data)

    venue_type = VenueType.objects(name_en=data["venue_type_en"].lower()).first()
    if not venue_type:
        raise UserError(f"Venue type '{data['venue_type_en']}' not found", 404)

    if "name_en" in data:
        source_lang = "en"
        source_text = data["name_en"]
    elif "name_he" in data:
        source_lang = "iw"  # Google Translate uses 'iw'
        source_text = data["name_he"]
    elif "name_ru" in data:
        source_lang = "ru"
        source_text = data["name_ru"]
    else:
        raise UserError("At least one 'name' in any language must be provided")

    name_en = data.get("name_en")
    name_ru = data.get("name_ru")
    name_he = data.get("name_he")

    if not name_en:
        target_lang = "en"
        name_en = translate_with_google(source_text, source_lang, target_lang)
    if not name_he:
        target_lang = "iw"
        name_he = translate_with_google(source_text, source_lang, target_lang)
    if not name_ru:
        target_lang = "ru"
        name_ru = translate_with_google(source_text, source_lang, target_lang)

    if "description_en" in data:
        source_lang = "en"
        source_text = data["description_en"]
    elif "description_he" in data:
        source_lang = "iw"  # Google Translate uses 'iw'
        source_text = data["description_he"]
    elif "description_ru" in data:
        source_lang = "ru"
        source_text = data["description_ru"]
    else:
        raise UserError("At least one 'description' in any language must be provided")

    description_en = data.get("description_en")
    description_ru = data.get("description_ru")
    description_he = data.get("description_he")

    if not description_en:
        target_lang = "en"
        description_en = translate_with_google(source_text, source_lang, target_lang)
    if not description_he:
        target_lang = "iw"
        description_he = translate_with_google(source_text, source_lang, target_lang)
    if not description_ru:
        target_lang = "ru"
        description_ru = translate_with_google(source_text, source_lang, target_lang)

    # if "name_en" in data:
    #     source_lang = "en-GB"
    #     source_text = data["name_en"]
    # elif "name_he" in data:
    #     source_lang = "he-IL"
    #     source_text = data["name_he"]
    # elif "name_ru" in data:
    #     source_lang = "ru-RU"
    #     source_text = data["name_ru"]
    # else:
    #     raise UserError("At least one 'name' in any language must be provided")
    #
    # name_en = data.get("name_en")
    # name_ru = data.get("name_ru")
    # name_he = data.get("name_he")
    #
    # if not name_en:
    #     name_en = translate_with_mymemory(source_text, source_lang, "en-GB")
    # if not name_he:
    #     name_he = translate_with_mymemory(source_text, source_lang, "he-IL")
    # if not name_ru:
    #     name_ru = translate_with_mymemory(source_text, source_lang, "ru-RU")
    #
    # if "description_en" in data:
    #     source_lang = "en-GB"
    #     source_text = data["description_en"]
    # elif "description_he" in data:
    #     source_lang = "he-IL"
    #     source_text = data["description_he"]
    # elif "description_ru" in data:
    #     source_lang = "ru-RU"
    #     source_text = data["description_ru"]
    # else:
    #     raise UserError("At least one 'description' in any language must be provided")
    #
    # description_en = data.get("description_en")
    # description_ru = data.get("description_ru")
    # description_he = data.get("description_he")
    #
    # if not description_en:
    #     description_en = translate_with_mymemory(source_text, source_lang, "en-GB")
    # if not description_he:
    #     description_he = translate_with_mymemory(source_text, source_lang, "he-IL")
    # if not description_ru:
    #     description_ru = translate_with_mymemory(source_text, source_lang, "ru-RU")

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
        name_en=name_en,
        name_ru=name_ru,
        name_he=name_he,
        address_en=address_data["en"],
        address_ru=address_data["ru"],
        address_he=address_data["he"],
        description_en=description_en,
        description_ru=description_ru,
        description_he=description_he,
        venue_type=venue_type,
        city=city,
        location=address_data["location"],
        phone=data.get("phone"),
        website=data.get("website"),
        slug=slugify(name_en)
    )

    if "image" in request.files:
        image_path = save_venue_image(file, venue.slug)
        venue.image_path = image_path

    venue.save()

    return jsonify({
        'status': 'success',
        'message': 'Venue created successfully',
        "data": venue.to_response_dict()
    }), 201
