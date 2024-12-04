from flask import request, jsonify
from slugify import slugify
from backend.src.models.city import City
from backend.src.models.venue import Venue
from backend.src.models.venue_type import VenueType
from backend.src.services.geonames_service import validate_and_get_names
from backend.src.services.here_service import validate_and_get_addr_and_location
from backend.src.services.translation_service import translate_with_google
from backend.src.utils.exceptions import UserError
from backend.src.utils.file_utils import validate_image, save_venue_image
from backend.src.config.experiments.language_utils import validate_language
from backend.src.utils.constants import ALLOWED_VENUE_BODY_PARAMS, STRICTLY_REQUIRED_VENUE_BODY_PARAMS
from backend.src.utils.pre_mongo_validators import validate_venue_data
from concurrent.futures import ThreadPoolExecutor


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
        name_source_lang = "en"
        name_source_text = data["name_en"]
    elif "name_he" in data:
        name_source_lang = "iw"  # Google Translate uses 'iw'
        name_source_text = data["name_he"]
    elif "name_ru" in data:
        name_source_lang = "ru"
        name_source_text = data["name_ru"]
    else:
        raise UserError("At least one 'name' in any language must be provided")

    name_en = data.get("name_en")
    name_ru = data.get("name_ru")
    name_he = data.get("name_he")

    if "description_en" in data:
        descr_source_lang = "en"
        descr_source_text = data["description_en"]
    elif "description_he" in data:
        descr_source_lang = "iw"  # Google Translate uses 'iw'
        descr_source_text = data["description_he"]
    elif "description_ru" in data:
        descr_source_lang = "ru"
        descr_source_text = data["description_ru"]
    else:
        raise UserError("At least one 'description' in any language must be provided")

    description_en = data.get("description_en")
    description_ru = data.get("description_ru")
    description_he = data.get("description_he")

    # Check if city exists, if not - try to add it
    city = City.objects(name_en=data["city_en"]).first()

    # -----
    new_city_names = None
    with ThreadPoolExecutor() as executor:
        # Запускаем и переводы, и геокодинг
        if not name_en:
            name_en_future = executor.submit(translate_with_google, name_source_text, name_source_lang, "en")
        if not name_ru:
            name_ru_future = executor.submit(translate_with_google, name_source_text, name_source_lang, "ru")
        if not name_he:
            name_he_future = executor.submit(translate_with_google, name_source_text, name_source_lang, "iw")

        if not description_en:
            description_en_future = executor.submit(translate_with_google, descr_source_text, descr_source_lang, "en")
        if not description_ru:
            description_ru_future = executor.submit(translate_with_google, descr_source_text, descr_source_lang, "ru")
        if not description_he:
            description_he_future = executor.submit(translate_with_google, descr_source_text, descr_source_lang, "iw")

        if not city:
            new_city_names_future = executor.submit(validate_and_get_names, data["city_en"])

        # Получаем результаты переводов
        if not name_en:
            name_en = name_en_future.result()
        if not name_ru:
            name_ru = name_ru_future.result()
        if not name_he:
            name_he = name_he_future.result()

        # --
        if not description_en:
            description_en = description_en_future.result()
        if not description_ru:
            description_ru = description_ru_future.result()
        if not description_he:
            description_he = description_he_future.result()

        # --
        if not city:
            new_city_names = new_city_names_future.result()


    # If city doesn't exist, add it using GeoNames
    if new_city_names:
        city = City(
            name_en=new_city_names["en"],
            name_ru=new_city_names["ru"],
            name_he=new_city_names["he"],
            slug=slugify(new_city_names["en"])
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
