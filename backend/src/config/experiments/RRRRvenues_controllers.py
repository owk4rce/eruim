from flask import request, jsonify
from slugify import slugify
from backend.src.models.city import City
from backend.src.models.venue import Venue
from backend.src.models.venue_type import VenueType
from backend.src.services.geonames_service import validate_and_get_names
from backend.src.services.here_service import validate_and_get_location
from backend.src.services.translation_service import translate_with_google, translate_with_mymemory
from backend.src.utils.exceptions import UserError
from backend.src.utils.file_utils import validate_image, delete_folder_from_path, save_image_from_request
from backend.src.utils.constants import (STRICTLY_REQUIRED_VENUE_CREATE_BODY_PARAMS, ALLOWED_VENUE_GET_ALL_ARGS,
                                         SUPPORTED_LANGUAGES, ALLOWED_VENUE_CREATE_BODY_PARAMS,
                                         ALLOWED_VENUE_UPDATE_BODY_PARAMS)
from backend.src.utils.pre_mongo_validators import validate_venue_data
from backend.src.utils.transliteration import transliterate_en_to_he, transliterate_en_to_ru
from backend.src.models.event import Event


def get_all_venues():
    """

    """
    # if request.data:
    #     raise UserError("Using body in GET-method is restricted.")

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

    """
    # if request.data:
    #     raise UserError("Using body in GET-method is restricted.")

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

    """
    file = None
    if request.content_type.startswith("multipart/form-data"):  # expecting file via form
        unknown_files = set(request.files.keys()) - {"image"}
        if unknown_files:
            raise UserError(f"Unknown files in request: {', '.join(unknown_files)}")

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

    return jsonify({
        'status': 'success',
        'message': 'Venue created successfully',
        "data": venue.to_response_dict()
    }), 201


def full_update_existing_venue(slug):
    """
    full update venue

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

    name_en = data["name_en"]
    name_ru = data["name_ru"]
    name_he = data["name_he"]

    description_en = data["description_en"]
    description_ru = data["description_ru"]
    description_he = data["description_he"]

    phone = data["phone"]
    website = data["website"]
    email = data["email"]

    address_ru = data['address_ru']
    address_he = data['address_he']
    address_en = data['address_en']

    if venue.address_en != address_en:
        # Find coordinates if core address_en changed
        full_address_he = f"{address_he}, {city.name_he}"

        location = validate_and_get_location(full_address_he)

        if venue.location["coordinates"] != location["coordinates"]:
            venue.location = location

    venue.name_ru = name_ru
    venue.name_he = name_he
    venue.name_en = name_en
    venue.address_en = address_en
    venue.address_ru = address_ru
    venue.address_he = address_he
    venue.description_en = description_en
    venue.description_ru = description_ru
    venue.description_he = description_he
    venue.venue_type = venue_type
    venue.city = city
    venue.phone = phone
    venue.website = website
    venue.email = email
    venue.is_active = is_active
    venue.slug = slugify(name_en)

    if "image" in request.files:
        image_path = save_image_from_request(file, "venues", venue.slug)
        venue.image_path = image_path

    venue.save()

    return jsonify({
        'status': 'success',
        'message': 'Venue fully updated successfully',
        "data": venue.to_response_dict()
    }), 200


def part_update_existing_venue(slug):
    """
    part update venue

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
    updated_fields = []
    unchanged_fields = []

    if "image" in request.files:
        image_path = save_image_from_request(file, "venues", venue.slug)
        venue.image_path = image_path
        updated_fields.append("image_path")

    # ---

    for param in data:
        match param:
            case "is_active":
                if data["is_active"] != venue.is_active:
                    if not data["is_active"] and venue.is_active:
                        active_events = Event.objects(venue=venue, is_active=True).count()
                        if active_events > 0:
                            raise UserError(
                                "Cannot deactivate venue with active events. Please deactivate all events first.",
                                409
                            )
                    setattr(venue, param, data["is_active"])
                    updated_fields.append("is_active")
                else:
                    unchanged_fields.append(param)
            case "venue_type_en":
                venue_type = VenueType.objects(name_en=data["venue_type_en"].lower()).first()

                if not venue_type:
                    raise UserError(f"Venue type '{data['venue_type_en']}' not found", 404)
                if venue.venue_type != venue_type:
                    setattr(venue, "venue_type", venue_type)
                    updated_fields.append("venue_type")
                else:
                    unchanged_fields.append(param)
            case "city_en":
                # Check if city exists
                city = City.objects(name_en=data["city_en"]).first()

                # If city doesn't exist, error
                if not city:
                    raise UserError(f"City '{data['city_en']}' not found", 404)
                if venue.city != city:
                    setattr(venue, "city", city)
                    updated_fields.append("city")
                else:
                    unchanged_fields.append(param)
            case _:
                current_value = getattr(venue, param)
                new_value = data[param]

                if current_value != new_value:
                    setattr(venue, param, new_value)
                    updated_fields.append(param)

                    match param:
                        # Check location if address_en changed
                        case "address_en":
                            # Find coordinates if core address_en changed
                            full_address_he = f"{venue.address_he}, {venue.city.name_he}"

                            location = validate_and_get_location(full_address_he)

                            if venue.location['coordinates'] != location['coordinates']:
                                venue.location = location
                                updated_fields.append("location")

                        # Update slug if English name changes
                        case "name_en":
                            venue.slug = slugify(new_value)
                            updated_fields.append("slug")
                else:
                    unchanged_fields.append(param)

    # ---

    # for param in data:
    #     if param == "is_active":
    #         if data["is_active"] != venue.is_active:
    #             if not data["is_active"] and venue.is_active:
    #                 active_events = Event.objects(venue=venue, is_active=True).count()
    #                 if active_events > 0:
    #                     raise UserError(
    #                         "Cannot deactivate venue with active events. Please deactivate all events first.",
    #                         409
    #                     )
    #             setattr(venue, param, data["is_active"])
    #             updated_fields.append("is_active")
    #         else:
    #             unchanged_fields.append(param)
    #     elif param == "venue_type_en":
    #         venue_type = VenueType.objects(name_en=data["venue_type_en"].lower()).first()
    #
    #         if not venue_type:
    #             raise UserError(f"Venue type '{data['venue_type_en']}' not found", 404)
    #         if venue.venue_type != venue_type:
    #             setattr(venue, "venue_type", venue_type)
    #             updated_fields.append("venue_type")
    #         else:
    #             unchanged_fields.append(param)
    #     elif param == "city_en":
    #         # Check if city exists
    #         city = City.objects(name_en=data["city_en"]).first()
    #
    #         # If city doesn't exist, error
    #         if not city:
    #             raise UserError(f"City '{data['city_en']}' not found", 404)
    #         if venue.city != city:
    #             setattr(venue, "city", city)
    #             updated_fields.append("city")
    #         else:
    #             unchanged_fields.append(param)
    #     else:
    #         current_value = getattr(venue, param)
    #         new_value = data[param]
    #
    #         if current_value != new_value:
    #             setattr(venue, param, new_value)
    #             updated_fields.append(param)
    #
    #             # Check location if address_en changed
    #             if param == "address_en":
    #                 # Find coordinates if core address_en changed
    #                 full_address_he = f"{venue.address_he}, {venue.city.name_he}"
    #
    #                 location = validate_and_get_location(full_address_he)
    #
    #                 if venue.location['coordinates'] != location['coordinates']:
    #                     venue.location = location
    #                     updated_fields.append("location")
    #
    #             # Update slug if English name changes
    #             if param == "name_en":
    #                 venue.slug = slugify(new_value)
    #                 updated_fields.append("slug")
    #         else:
    #             unchanged_fields.append(param)

    if updated_fields:
        venue.save()
        message = f"Updated fields: {', '.join(updated_fields)}"
        if unchanged_fields:
            message += f". Unchanged fields: {', '.join(unchanged_fields)}"
    else:
        message = "No fields were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": venue.to_response_dict()
    }), 200


def delete_existing_venue(slug):
    """

    """
    # if request.data:
    #     raise UserError("Using body in DELETE-method is restricted.")

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
