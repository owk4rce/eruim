from flask import request, jsonify
from slugify import slugify

from backend.src.models.city import City
from backend.src.models.venue import Venue
from backend.src.services.translation_service import translate_with_google
from backend.src.utils.exceptions import UserError
from backend.src.utils.file_utils import validate_image, delete_folder_from_path, \
    save_image_from_request, rename_image_folder
from backend.src.utils.constants import (SUPPORTED_LANGUAGES, ALLOWED_EVENT_GET_ALL_ARGS,
                                         ALLOWED_EVENT_CREATE_BODY_PARAMS, STRICTLY_REQUIRED_EVENT_CREATE_BODY_PARAMS,
                                         ALLOWED_EVENT_UPDATE_BODY_PARAMS)
from backend.src.utils.pre_mongo_validators import validate_event_data
from backend.src.utils.transliteration import transliterate_en_to_he, transliterate_en_to_ru
from backend.src.models.event import Event
from backend.src.models.event_type import EventType
from backend.src.utils.date_utils import convert_to_utc, convert_to_local, remove_timezone

import logging
logger = logging.getLogger("backend")


def get_all_events():
    """
    Get filtered list of events.

    Query params:
        lang (optional): Response language (en/ru/he)
        is_active (optional): Filter by active status
        city (optional): Filter by city slug
        venue (optional): Filter by venue slug
        sort (optional): Sort by date (asc/desc)

    Note: city and venue filters are mutually exclusive
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

    city_slug_arg = request.args.get("city")
    venue_slug_arg = request.args.get("venue")

    if city_slug_arg and venue_slug_arg:
        raise UserError("Only one argument, 'city' or 'venue', is allowed. ")

    # if city filter
    if city_slug_arg:
        city = City.objects(slug=city_slug_arg).first()
        if not city:
            raise UserError(f"City with slug '{city_slug_arg}' not found.", 404)

        venues = Venue.objects(city=city)
        query["venue__in"] = venues

    # if venue filter
    if venue_slug_arg:
        venue = Venue.objects(slug=venue_slug_arg).first()
        if not venue:
            raise UserError(f"Venue with slug '{venue_slug_arg}' not found.", 404)

        query["venue"] = venue

    # Handle sorting by start_date (desc by default to show upcoming events first)
    sort_direction = request.args.get("sort", "desc")
    if sort_direction not in ["asc", "desc"]:
        raise UserError("Parameter 'sort' must be 'asc' or 'desc'")

    # Convert sort direction to mongoengine format (+/-)
    sort_prefix = "" if sort_direction == "asc" else "-"

    # Get events from database with filters and sorting
    events = Event.objects(**query).order_by(f"{sort_prefix}start_date")

    # format response
    events_data = [event.to_response_dict(lang_arg) for event in events]

    return jsonify({
        "status": "success",
        "data": events_data,
        "count": len(events_data)
    }), 200


def get_existing_event(slug):
    """
    Get single event by slug.

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
    Create new event with auto-translation.

    Accepts multipart/form-data or application/json.
    Required fields:
        - venue_slug
        - event_type_slug
        - start_date (YYYY-MM-DD HH:MM or YYYY-MM-DD)
        - end_date
        - price_type (free/tba/fixed/starting_from)
    Optional fields:
        - At least one name (name_en/name_ru/name_he)
        - At least one description
        - price_amount (required for fixed/starting_from)
        - image file

    Process:
        1. Validates all data and image if present
        2. Auto-translates missing languages
        3. Saves image if provided
        4. Creates event with generated slug (name_en + date)
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

    data["start_date"] = convert_to_utc(data["start_date"])
    data["end_date"] = convert_to_utc(data["end_date"], False)

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

    # date format for slug
    local_date = convert_to_local(data.get("start_date"))
    slug_date = local_date.strftime('%Y-%m-%d-%H-%M')

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
    event.reload()  # correct time (while saving it is in our timezone but stores in utc)

    logger.info(f"Created new event: {name_en}")

    return jsonify({
        "status": "success",
        "message": "Event created successfully.",
        "data": event.to_response_dict()
    }), 201


def full_update_existing_event(slug):
    """
    Full update of event.

    Accepts multipart/form-data or application/json.
    Required all fields:
        - venue_slug, event_type_slug
        - start/end dates
        - names and descriptions in all languages
        - price_type and amount if needed
        - is_active
    Optional:
        - new image file

    Process:
        1. Validates all data
        2. Updates image if provided
        3. Updates slug if name or date changed
        4. Updates all fields
    """
    file = None
    if request.content_type.startswith("multipart/form-data"):  # expecting file via form
        unknown_files = set(request.files.keys()) - {"image"}
        if unknown_files:
            raise UserError(f"Unknown files in request: {', '.join(unknown_files)}")

        data = request.form.to_dict()
        if not data:
            raise UserError("Form data is empty.")

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

    data["start_date"] = convert_to_utc(data["start_date"])
    data["end_date"] = convert_to_utc(data["end_date"], False)

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
    event.start_date = data["start_date"]
    event.end_date = data["end_date"]
    event.price_type = data["price_type"]
    event.price_amount = data.get("price_amount")
    event.is_active = data["is_active"]

    # date format for slug
    local_date = convert_to_local(data["start_date"])
    slug_date = local_date.strftime('%Y-%m-%d-%H-%M')

    new_slug = slugify(f"{data['name_en']}-{slug_date}")

    if new_slug != event.slug and not event.image_path.endswith("default.png"):
        new_image_path = rename_image_folder("events", event.slug, new_slug)
        event.image_path = new_image_path

    event.slug = new_slug

    if "image" in request.files:
        image_path = save_image_from_request(file, "events", event.slug)
        event.image_path = image_path

    event.save()
    event.reload()  # correct time (while saving it is in our timezone but stores in utc)

    logger.info(f"Full update of event: {event.name_en}")

    return jsonify({
        "status": "success",
        "message": "Event fully updated successfully",
        "data": event.to_response_dict()
    }), 200


def part_update_existing_event(slug):
    """
    Partial update of event.

    Accepts multipart/form-data or application/json.
    Optional fields:
        - Any event field to update
        - New image file

    Process:
        1. Validates provided data
        2. Updates only changed fields
        3. Updates slug if name or date changed
        4. Tracks and reports changed/unchanged fields
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

        if "price_amount" in data:  # converting str to int if it matches
            if data["price_amount"].isdigit():
                data["price_amount"] = int(data["price_amount"])
            else:
                raise UserError("Parameter 'price_amount' must be a number.")
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

    if "start_date" in data and "end_date" not in data:
        data["start_date"] = remove_timezone(convert_to_utc(data["start_date"]))
        data["end_date"] = event.end_date
    elif "end_date" in data and "start_date" not in data:
        data["start_date"] = event.start_date
        data["end_date"] = remove_timezone(convert_to_utc(data["end_date"], False))
    elif "start_date" in data and "end_date" in data:
        data["start_date"] = remove_timezone(convert_to_utc(data["start_date"]))
        data["end_date"] = remove_timezone(convert_to_utc(data["end_date"], False))

    validate_event_data(data)  # we need both of dates or none of them

    # Track changes
    updated_params = []
    unchanged_params = []

    for param, value in data.items():
        match param:
            case "event_type_slug":
                event_type = EventType.objects(slug=value).first()

                if not event_type:
                    raise UserError(f"Event type with slug '{value}' not found.", 404)
                if event.event_type != event_type:
                    setattr(event, "event_type", event_type)
                    updated_params.append("event_type")
                else:
                    unchanged_params.append("event_type")
            case "venue_slug":
                venue = Venue.objects(slug=value).first()

                if not venue:
                    raise UserError(f"Venue with slug '{value}' not found.", 404)
                if event.venue != venue:
                    setattr(event, "venue", venue)
                    updated_params.append("venue")
                else:
                    unchanged_params.append("venue")
            case _:
                current_value = getattr(event, param)

                if current_value != value:
                    setattr(event, param, value)
                    updated_params.append(param)
                else:
                    unchanged_params.append(param)

    if "image" in request.files:
        image_path = save_image_from_request(file, "events", event.slug)
        event.image_path = image_path
        updated_params.append("image_path")

    if updated_params:
        # Update slug if English name or start_date changes
        if "start_date" in updated_params or "name_en" in updated_params:
            # date format for slug
            local_date = convert_to_local(data.get("start_date", event.start_date))
            slug_date = local_date.strftime('%Y-%m-%d-%H-%M')
            name_en = data["name_en"] if "name_en" in data else event.name_en
            new_slug = slugify(f"{name_en}-{slug_date}")

            if new_slug != event.slug and not event.image_path.endswith('default.png'):
                new_image_path = rename_image_folder('events', event.slug, new_slug)
                event.image_path = new_image_path

            event.slug = new_slug

        event.save()
        event.reload()  # correct time (while saving it is in our timezone but stores in utc)
        logger.info(f"Partial update of event {event.name_en}, fields: {', '.join(updated_params)}")
        message = f"Updated parameters: {', '.join(updated_params)}"
        if unchanged_params:
            message += f". Unchanged parameters: {', '.join(unchanged_params)}"
    else:
        message = "No parameters were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": event.to_response_dict()
    }), 200


def delete_existing_event(slug):
    """
    Delete event and its image files.
    """

    # Find existing event
    event = Event.objects(slug=slug).first()
    if not event:
        raise UserError(f"Event with slug '{slug}' not found", 404)

    logger.info(f"Deleting event: {event.name_en}")

    # delete the event and image from image_path
    delete_folder_from_path(event.image_path)
    event.delete()

    # Return 204 No Content for successful deletion
    return '', 204
