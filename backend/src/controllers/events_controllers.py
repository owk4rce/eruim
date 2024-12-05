from flask import request, jsonify
from slugify import slugify
from datetime import datetime

from backend.src.models.city import City
from backend.src.models.venue import Venue
from backend.src.models.venue_type import VenueType
from backend.src.services.here_service import validate_and_get_location
from backend.src.services.translation_service import translate_with_google, translate_with_mymemory
from backend.src.utils.exceptions import UserError
from backend.src.utils.file_utils import validate_image, delete_folder_from_path, \
    save_image_from_request
from backend.src.utils.constants import (SUPPORTED_LANGUAGES,
                                         ALLOWED_VENUE_UPDATE_BODY_PARAMS, ALLOWED_EVENT_GET_ALL_ARGS,
                                         ALLOWED_EVENT_CREATE_BODY_PARAMS, STRICTLY_REQUIRED_EVENT_CREATE_BODY_PARAMS,
                                         ALLOWED_EVENT_UPDATE_BODY_PARAMS, TIMEZONE)
from backend.src.utils.pre_mongo_validators import validate_venue_data, validate_event_data
from backend.src.utils.transliteration import transliterate_en_to_he, transliterate_en_to_ru
from backend.src.models.event import Event
from backend.src.models.event_type import EventType


def get_all_events():
    """

    """

    unknown_args = set(request.args.keys()) - ALLOWED_EVENT_GET_ALL_ARGS
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    # Get language preference from query parameter
    lang_arg = request.args.get("lang")
    if lang_arg:
        if lang_arg not in SUPPORTED_LANGUAGES:
            raise UserError(f"Unsupported language: {lang_arg}")

    # Start with base query (to collect all parameter)
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

    # Get events from database with filters
    events = Event.objects(**query)

    # format response
    events_data = [event.to_response_dict(lang_arg) for event in events]

    return jsonify({
        "status": "success",
        "data": events_data,
        "count": len(events_data)
    }), 200


def get_existing_event(slug):
    """

    """
    unknown_args = set(request.args.keys()) - {"lang"}
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    # Get language preference from query parameter
    lang_arg = request.args.get("lang")
    if lang_arg:
        if lang_arg not in SUPPORTED_LANGUAGES:
            raise UserError(f"Unsupported language: {lang_arg}")

    # Get one event from database
    event = Event.objects(slug=slug).first()

    if not event:
        raise UserError(f"Event with slug {slug} not found.", 404)

    # format response
    event_data = event.to_response_dict(lang_arg)

    return jsonify({
        "status": "success",
        "data": event_data
    }), 200


def create_new_event():
    """

    """
    file = None
    if request.content_type.startswith("multipart/form-data"):  # expecting file via form
        unknown_files = set(request.files.keys()) - {"image"}
        if unknown_files:
            raise UserError(f"Unknown files in request: {', '.join(unknown_files)}")

        data = request.form.to_dict()
        if not data:
            raise UserError("Form data is empty.")

        if "price_amount" in data:  # converting str to int if it matches
            if data["price_amount"].isdigit():
                data["price_amount"] = int(data["price_amount"])
            else:
                raise UserError("Parameter 'price_amount' must be a number.")

        if "image" in request.files:
            file = request.files["image"]
            validate_image(file)
    elif not request.is_json:
        raise UserError("Content-Type must be either multipart/form-data or application/json", 415)
    else:
        data = request.get_json()
        if not data:
            raise UserError("JSON body is empty")

    unknown_params = set(data.keys()) - ALLOWED_EVENT_CREATE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = STRICTLY_REQUIRED_EVENT_CREATE_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    # date format for slug
    slug_date = data['start_date'].replace(' ', '-')

    try:
        data["start_date"] = datetime.strptime(data["start_date"], '%Y-%m-%d %H:%M')
        data["end_date"] = datetime.strptime(data["end_date"], '%Y-%m-%d %H:%M')
    except ValueError:
        raise UserError('Invalid date format. Use YYYY-MM-DD HH:MM')

    validate_event_data(data)

    event_type = EventType.objects(slug=data["event_type_slug"]).first()
    if not event_type:
        raise UserError(f"Event type with slug '{data['event_type_slug']}' not found.", 404)

    venue = Venue.objects(slug=data["venue_slug"].lower()).first()
    if not venue:
        raise UserError(f"Venue with slug '{data['venue_slug']}' not found.", 404)

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
        raise UserError("At least one 'name' in any language must be provided.")

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
        raise UserError("At least one 'description' in any language must be provided.")

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

    # for the cases of non-translated abbreviations like ANU
    name_he = transliterate_en_to_he(name_he)
    name_ru = transliterate_en_to_ru(name_ru)

    description_he = transliterate_en_to_he(description_he)
    description_ru = transliterate_en_to_ru(description_ru)

    event = Event(
        name_en=name_en,
        name_ru=name_ru,
        name_he=name_he,
        description_en=description_en,
        description_ru=description_ru,
        description_he=description_he,
        event_type=event_type,
        venue=venue,
        start_date=data["start_date"],
        end_date=data["end_date"],
        price_type=data["price_type"],
        price_amount=data.get("price_amount"),
        slug=slugify(f"{name_en}-{slug_date}")
    )

    if "image" in request.files:
        image_path = save_image_from_request(file, "events", event.slug)
        event.image_path = image_path

    event.save()

    return jsonify({
        'status': 'success',
        'message': 'Event created successfully.',
        "data": event.to_response_dict()
    }), 201


def full_update_existing_event(slug):
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

        if "price_amount" in data:  # converting str to int if it matches
            if data["price_amount"].isdigit():
                data["price_amount"] = int(data["price_amount"])
            else:
                raise UserError("Parameter 'price_amount' must be a number.")

        if "image" in request.files:
            file = request.files["image"]
            validate_image(file)
    elif not request.is_json:
        raise UserError("Content-Type must be either multipart/form-data or application/json", 415)
    else:
        data = request.get_json()
        if not data:
            raise UserError("JSON body is empty")

    event = Event.objects(slug=slug).first()
    if not event:
        raise UserError(f"Event with slug '{slug}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_EVENT_UPDATE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = ALLOWED_EVENT_UPDATE_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    # date format for slug
    slug_date = data['start_date'].replace(' ', '-')

    try:
        data["start_date"] = datetime.strptime(data["start_date"], '%Y-%m-%d %H:%M')
        data["end_date"] = datetime.strptime(data["end_date"], '%Y-%m-%d %H:%M')
    except ValueError:
        raise UserError('Invalid date format. Use YYYY-MM-DD HH:MM')

    validate_event_data(data)

    event_type = EventType.objects(slug=data["event_type_slug"]).first()
    if not event_type:
        raise UserError(f"Event type with slug '{data['event_type_slug']}' not found.", 404)

    venue = Venue.objects(slug=data["venue_slug"].lower()).first()
    if not venue:
        raise UserError(f"Venue with slug '{data['venue_slug']}' not found.", 404)

    event.name_en = data["name_en"]
    event.name_ru = data["name_ru"]
    event.name_he = data["name_he"]
    event.description_en = data["description_en"]
    event.description_ru = data["description_ru"]
    event.description_he = data["description_he"]
    event.event_type = event_type
    event.venue = venue
    event.start_date = TIMEZONE.localize(data["start_date"])
    event.end_date = TIMEZONE.localize(data["end_date"])
    event.price_type = data["price_type"]
    event.price_amount = data.get("price_amount")
    event.is_active = data['is_active']
    event.slug = slugify(f"{data['name_en']}-{slug_date}")

    if "image" in request.files:
        image_path = save_image_from_request(file, "events", event.slug)
        event.image_path = image_path

    event.save()
    event.reload()

    return jsonify({
        'status': 'success',
        'message': 'Event fully updated successfully',
        "data": event.to_response_dict()
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
        image_path = save_venue_image(file, venue.slug)
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
