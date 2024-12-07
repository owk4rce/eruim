from flask import request, jsonify
from slugify import slugify
from backend.src.models.city import City
from backend.src.models.venue import Venue
from backend.src.models.venue_type import VenueType
from backend.src.services.geonames_service import validate_and_get_names
from backend.src.services.here_service import validate_and_get_location
from backend.src.services.translation_service import translate_with_google
from backend.src.utils.exceptions import UserError
from backend.src.utils.file_utils import validate_image, delete_folder_from_path, save_image_from_request, \
    rename_image_folder
from backend.src.utils.constants import (STRICTLY_REQUIRED_VENUE_CREATE_BODY_PARAMS, ALLOWED_VENUE_GET_ALL_ARGS,
                                         SUPPORTED_LANGUAGES, ALLOWED_VENUE_CREATE_BODY_PARAMS,
                                         ALLOWED_VENUE_UPDATE_BODY_PARAMS)
from backend.src.utils.pre_mongo_validators import validate_venue_data
from backend.src.utils.transliteration import transliterate_en_to_he, transliterate_en_to_ru
from backend.src.models.event import Event

import logging
logger = logging.getLogger('backend')


def get_all_venues():
    """
    Get filtered list of venues.

    Query params:
        lang (optional): Response language (en/ru/he)
        is_active (optional): Filter by active status
        city (optional): Filter by city slug
    """
    unknown_args = set(request.args.keys()) - ALLOWED_VENUE_GET_ALL_ARGS
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    # Get language preference from query parameter
    lang_arg = request.args.get("lang")
    if lang_arg:
        if lang_arg not in SUPPORTED_LANGUAGES:
            raise UserError(f"Unsupported language: {lang_arg}")

    # Start with base query
    query = {}

    # Add is_active filter if provided
    is_active_arg = request.args.get("is_active")
    if is_active_arg:
        match is_active_arg.lower():
            case "true":
                query["is_active"] = True
            case "false":
                query["is_active"] = False
            case _:
                raise UserError("Parameter 'is_active' must be 'true' or 'false'")

    city_slug_arg = request.args.get("city")
    if city_slug_arg:
        city = City.objects(slug=city_slug_arg).first()
        if not city:
            raise UserError(f"City with slug '{city_slug_arg}' not found", 404)
        query["city"] = city

    # Get venues from database with filters
    venues = Venue.objects(**query)

    # format response
    venues_data = [venue.to_response_dict(lang_arg) for venue in venues]

    return jsonify({
        "status": "success",
        "data": venues_data,
        "count": len(venues_data)
    }), 200


def get_existing_venue(slug):
    """
    Get single venue by slug.

    Query params:
        lang (optional): Response language (en/ru/he)
    """
    unknown_args = set(request.args.keys()) - {"lang"}
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    # Get language preference from query parameter
    lang_arg = request.args.get("lang")
    if lang_arg:
        if lang_arg not in SUPPORTED_LANGUAGES:
            raise UserError(f"Unsupported language: {lang_arg}")

    # Get one venue from database
    venue = Venue.objects(slug=slug).first()

    if not venue:
        raise UserError(f"Venue with slug {slug} not found.", 404)

    # format response
    venue_data = venue.to_response_dict(lang_arg)

    return jsonify({
        "status": "success",
        "data": venue_data
    }), 200


def create_new_venue():
    """
    Create new venue with auto-translation and geocoding.

    Accepts multipart/form-data or application/json.
    Required fields:
        - address_en
        - city_en
        - venue_type_en
    Optional fields:
        - At least one name (name_en/name_ru/name_he)
        - At least one description
        - contact info (phone/email/website)
        - image file

    Process:
        1. Validates all data and image
        2. Auto-translates missing languages
        3. Validates/creates city if needed
        4. Gets coordinates from HERE API
        5. Saves image if provided
        6. Creates venue with generated slug
    """
    file = None
    if request.content_type.startswith("multipart/form-data"):  # expecting file via form
        unknown_files = set(request.files.keys()) - {"image"}
        if unknown_files:
            raise UserError(f"Unknown files in request: {', '.join(unknown_files)}")

        data = request.form.to_dict()
        if not data:
            raise UserError("Form data is empty.")

        if "image" in request.files:
            file = request.files["image"]
            validate_image(file)
    elif not request.is_json:
        raise UserError("Content-Type must be either multipart/form-data or application/json", 415)
    else:
        data = request.get_json()
        if not data:
            raise UserError("JSON body is empty")

    unknown_params = set(data.keys()) - ALLOWED_VENUE_CREATE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = STRICTLY_REQUIRED_VENUE_CREATE_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    validate_venue_data(data)

    venue_type = VenueType.objects(name_en=data["venue_type_en"].lower()).first()
    if not venue_type:
        raise UserError(f"Venue type '{data['venue_type_en']}' not found", 404)

    if "name_en" in data:
        # Check if 'name_en' already in use
        if Venue.objects(name_en=data["name_en"]).first():
            raise UserError(f"Venue with name '{data['name_en']}' already exists", 409)
        source_lang = "en"
        source_text = data["name_en"]
    elif "name_he" in data:
        # Check if 'name_he' already in use
        if Venue.objects(name_he=data["name_he"]).first():
            raise UserError(f"Venue with name '{data['name_he']}' already exists", 409)
        source_lang = "iw"  # Google Translate uses 'iw'
        source_text = data["name_he"]
    elif "name_ru" in data:
        # Check if 'name_ru' already in use
        if Venue.objects(name_he=data["name_ru"]).first():
            raise UserError(f"Venue with name '{data['name_ru']}' already exists", 409)
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

        logger.info(f"Created new city during venue creation: {names['en']}")

    address_en = data["address_en"]

    # Translate address to Hebrew and combine with Hebrew city name
    address_he = translate_with_google(address_en, 'en', 'iw')
    full_address_he = f"{address_he}, {city.name_he}"

    location = validate_and_get_location(full_address_he)

    # Get Russian address translation
    address_ru = translate_with_google(address_he, 'iw', 'ru')

    # for the cases of non-translated abbreviations like ANU
    name_he = transliterate_en_to_he(name_he)
    name_ru = transliterate_en_to_ru(name_ru)

    description_he = transliterate_en_to_he(description_he)
    description_ru = transliterate_en_to_ru(description_ru)

    venue = Venue(
        name_en=name_en,
        name_ru=name_ru,
        name_he=name_he,
        address_en=address_en,
        address_ru=address_ru,
        address_he=address_he,
        description_en=description_en,
        description_ru=description_ru,
        description_he=description_he,
        venue_type=venue_type,
        city=city,
        location=location,
        phone=data.get("phone"),
        website=data.get("website"),
        email=data.get("email"),
        slug=slugify(name_en)
    )

    if "image" in request.files:
        image_path = save_image_from_request(file, "venues", venue.slug)
        venue.image_path = image_path

    venue.save()

    logger.info(f"Created new venue: {name_en} in {city.name_en}")

    return jsonify({
        'status': 'success',
        'message': 'Venue created successfully',
        "data": venue.to_response_dict()
    }), 201


def full_update_existing_venue(slug):
    """
    Full update of venue.

    Accepts multipart/form-data or application/json.
    Required all fields:
        - names, descriptions in all languages
        - address_en, city_en, venue_type_en
        - is_active
        - contact info
    Optional:
        - new image file

    Process:
        1. Validates all data
        2. Updates location if address changed
        3. Updates image and paths if provided
        4. Updates all fields atomically
    """
    file = None
    if request.content_type.startswith("multipart/form-data"):  # expecting file via form
        unknown_files = set(request.files.keys()) - {"image"}
        if unknown_files:
            raise UserError(f"Unknown files in request: {', '.join(unknown_files)}")

        data = request.form.to_dict()
        if not data:
            raise UserError("Form data is empty")

        if "is_active" in data:  # converting str to bool if it matches
            match data["is_active"].lower():
                case "true":
                    data["is_active"] = True  # type: ignore
                case "false":
                    data["is_active"] = False  # type: ignore
                case _:
                    raise UserError("Parameter 'is_active' must be 'true' or 'false'")

        if "image" in request.files:
            file = request.files["image"]
            validate_image(file)
    elif not request.is_json:
        raise UserError("Content-Type must be either multipart/form-data or application/json", 415)
    else:
        data = request.get_json()
        if not data:
            raise UserError("JSON body is empty")

    venue = Venue.objects(slug=slug).first()
    if not venue:
        raise UserError(f"Venue with slug '{slug}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_VENUE_UPDATE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = ALLOWED_VENUE_UPDATE_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    validate_venue_data(data)

    is_active = data['is_active']

    if not is_active and venue.is_active:
        active_events = Event.objects(venue=venue, is_active=True).count()
        if active_events > 0:
            raise UserError(
                "Cannot deactivate venue with active events. Please deactivate all events first.",
                409
            )

    venue_type = VenueType.objects(name_en=data["venue_type_en"].lower()).first()
    if not venue_type:
        raise UserError(f"Venue type '{data['venue_type_en']}' not found", 404)

    # Check if city exists
    city = City.objects(name_en=data["city_en"]).first()

    # If city doesn't exist, error
    if not city:
        raise UserError(f"City '{data['city_en']}' not found", 404)

    # Calculate new slug once
    new_slug = slugify(data["name_en"])

    # collecting simple updates
    update_data = {
        "set__name_en": data["name_en"],
        "set__name_ru": data["name_ru"],
        "set__name_he": data["name_he"],
        "set__description_en": data["description_en"],
        "set__description_ru": data["description_ru"],
        "set__description_he": data["description_he"],
        "set__address_en": data["address_en"],
        "set__address_ru": data["address_ru"],
        "set__address_he": data["address_he"],
        "set__phone": data["phone"],
        "set__website": data["website"],
        "set__email": data["email"],
        "set__is_active": is_active,
        "set__venue_type": venue_type,
        "set__city": city,
        "set__slug": new_slug
    }

    # Check if slug changed and update image path is needed
    if venue.slug != new_slug and not venue.image_path.endswith('default.png'):
        new_image_path = rename_image_folder('venues', venue.slug, new_slug)
        update_data["set__image_path"] = new_image_path

    if venue.address_en != data['address_en']:
        # Find coordinates if core address_en changed
        full_address_he = f"{data['address_he']}, {city.name_he}"

        location = validate_and_get_location(full_address_he)

        if venue.location["coordinates"] != location["coordinates"]:
            update_data["set__location"] = location

    if "image" in request.files:
        image_path = save_image_from_request(file, "venues", venue.slug)
        update_data["set__image_path"] = image_path

    # atomic update
    Venue.objects(slug=slug).update_one(**update_data)

    # reload to get new for response
    venue.reload()

    logger.info(f"Full update of venue: {venue.name_en}")

    return jsonify({
        'status': 'success',
        'message': 'Venue fully updated successfully',
        "data": venue.to_response_dict()
    }), 200


def part_update_existing_venue(slug):
    """
    Partial update of venue.

    Accepts multipart/form-data or application/json.
    Optional fields:
        - Any venue field to update
        - New image file

    Process:
        1. Validates provided fields
        2. Updates location if address changed
        3. Updates image and paths if needed
        4. Updates only changed fields
    """
    file = None
    if request.content_type.startswith("multipart/form-data"):  # expecting file via form
        unknown_files = set(request.files.keys()) - {"image"}
        if unknown_files:
            raise UserError(f"Unknown files in request: {', '.join(unknown_files)}")

        data = request.form.to_dict()

        if "image" in request.files:
            file = request.files["image"]
            validate_image(file)

        # Check if neither data nor file was provided
        if not data and not file:
            raise UserError("Neither form data nor file provided.")

        if "is_active" in data:  # converting str to bool if it matches
            match data["is_active"].lower():
                case "true":
                    data["is_active"] = True  # type: ignore
                case "false":
                    data["is_active"] = False  # type: ignore
                case _:
                    raise UserError("Parameter 'is_active' must be 'true' or 'false'")
    elif not request.is_json:
        raise UserError("Content-Type must be either multipart/form-data or application/json", 415)
    else:
        data = request.get_json()
        if not data:
            raise UserError("JSON body is empty")

    unknown_params = set(data.keys()) - ALLOWED_VENUE_UPDATE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    validate_venue_data(data)

    venue = Venue.objects(slug=slug).first()
    if not venue:
        raise UserError(f"Venue with slug '{slug}' not found", 404)

    # Track changes
    update_data = {}
    unchanged_params = []

    for param, value in data.items():
        match param:
            case "is_active":
                if value != venue.is_active:
                    if not value and venue.is_active:
                        active_events = Event.objects(venue=venue, is_active=True).count()
                        if active_events > 0:
                            raise UserError(
                                "Cannot deactivate venue with active events. Please deactivate all events first.",
                                409
                            )
                    update_data["set__is_active"] = value
                else:
                    unchanged_params.append(param)
            case "venue_type_en":
                venue_type = VenueType.objects(name_en=data["venue_type_en"].lower()).first()

                if not venue_type:
                    raise UserError(f"Venue type '{data['venue_type_en']}' not found", 404)
                if venue.venue_type != venue_type:
                    update_data["set__venue_type"] = venue_type
                else:
                    unchanged_params.append("venue_type")
            case "city_en":
                # Check if city exists
                city = City.objects(name_en=data["city_en"]).first()

                # If city doesn't exist, error
                if not city:
                    raise UserError(f"City '{data['city_en']}' not found", 404)
                if venue.city != city:
                    update_data["set__city"] = city
                else:
                    unchanged_params.append("city")
            case "address_en":
                # Check if address_en changed
                if value != venue.address_en:
                    update_data["set__address_en"] = value

                    # Find coordinates if core address_en changed
                    full_address_he = f"{venue.address_he}, {venue.city.name_he}"

                    location = validate_and_get_location(full_address_he)

                    # if coordinates changed
                    if venue.location['coordinates'] != location['coordinates']:
                        update_data["set__location"] = location
                else:
                    unchanged_params.append(param)
            case "name_en":
                # Check if name_en changed
                if value != venue.name_en:
                    update_data["set__name_en"] = value
                    new_slug = slugify(value)
                    update_data["set__slug"] = new_slug
                    if not venue.image_path.endswith('default.png'):
                        new_image_path = rename_image_folder('venues', venue.slug, new_slug)
                        update_data["set__image_path"] = new_image_path
                else:
                    unchanged_params.append(param)
            case _:
                current_value = getattr(venue, param)

                if current_value != value:
                    update_data[f"set__{param}"] = value
                else:
                    unchanged_params.append(param)

    if "image" in request.files:
        image_path = save_image_from_request(file, "venues", venue.slug)
        update_data["set__image_path"] = image_path

    if update_data:
        Venue.objects(slug=slug).update_one(**update_data)
        venue.reload()
        updated_params = [param.replace('set__', '') for param in update_data.keys()]
        logger.info(f"Partial update of venue {venue.name_en}, fields: {', '.join(updated_params)}")
        message = f"Updated parameters: {', '.join(updated_params)}"
        if unchanged_params:
            message += f". Unchanged parameters: {', '.join(unchanged_params)}"
    else:
        message = "No parameters were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": venue.to_response_dict()
    }), 200


def delete_existing_venue(slug):
    """

    """
    # Find existing venue type
    venue = Venue.objects(slug=slug).first()
    if not venue:
        raise UserError(f"Venue with slug '{slug}' not found", 404)

    associated_active_events = Event.objects(venue=venue, is_active=True).count()

    if associated_active_events > 0:
        raise UserError(
            "Cannot delete venue with active events.",
            409
        )

    # If no active associated venues, delete the venue and image from image_path
    delete_folder_from_path(venue.image_path)
    venue.delete()  # cascade deleting of events (implemented in model Event)

    # Return 204 No Content for successful deletion
    return '', 204
