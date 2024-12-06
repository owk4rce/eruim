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

    city_slug_arg = request.args.get("city")
    venue_slug_arg = request.args.get("venue")

    if city_slug_arg and venue_slug_arg:
        raise UserError("Only one argument, 'city' or 'venue', is allowed. ")

    if city_slug_arg:
        city = City.objects(slug=city_slug_arg).first()
        if not city:
            raise UserError(f"City with slug '{city_slug_arg}' not found.", 404)

        venues = Venue.objects(city=city)
        query["venue__in"] = venues

    if venue_slug_arg:
        venue = Venue.objects(slug=venue_slug_arg).first()
        if not venue:
            raise UserError(f"Venue with slug '{venue_slug_arg}' not found.", 404)

        query["venue"] = venue

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
        start_date=TIMEZONE.localize(data["start_date"]),
        end_date=TIMEZONE.localize(data["end_date"]),
        price_type=data["price_type"],
        price_amount=data.get("price_amount"),
        slug=slugify(f"{name_en}-{slug_date}")
    )

    if "image" in request.files:
        image_path = save_image_from_request(file, "events", event.slug)
        event.image_path = image_path

    event.save()
    event.reload()  # correct time (while saving it is in our timezone but stores in utc)

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
    event.reload()  # correct time (while saving it is in our timezone but stores in utc)

    return jsonify({
        'status': 'success',
        'message': 'Event fully updated successfully',
        "data": event.to_response_dict()
    }), 200


def part_update_existing_event(slug):
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

    try:
        if "start_date" in data and "end_date" not in data:
            data["start_date"] = datetime.strptime(data["start_date"], '%Y-%m-%d %H:%M')
            data["end_date"] = event.end_date
        if "end_date" in data and "start_date" not in data:
            data["start_date"] = event.start_date
            data["end_date"] = datetime.strptime(data["end_date"], '%Y-%m-%d %H:%M')
    except ValueError:
        raise UserError('Invalid date format. Use YYYY-MM-DD HH:MM')

    validate_event_data(data)  # we need both of dates or none of them

    # Track changes
    updated_fields = []
    unchanged_fields = []

    if "image" in request.files:
        image_path = save_image_from_request(file, "events", event.slug)
        event.image_path = image_path
        updated_fields.append("image_path")

    for param in data:
        match param:
            case "event_type_slug":
                event_type = EventType.objects(slug=data["event_type_slug"]).first()

                if not event_type:
                    raise UserError(f"Event type with slug '{data['event_type_slug']}' not found.", 404)
                if event.event_type != event_type:
                    setattr(event, "event_type", event_type)
                    updated_fields.append("venue_type")
                else:
                    unchanged_fields.append(param)
            case "venue_slug":
                venue = Venue.objects(slug=data["venue_slug"]).first()

                if not venue:
                    raise UserError(f"Venue with slug '{data['venue_slug']}' not found.", 404)
                if event.venue != venue:
                    setattr(event, "venue", venue)
                    updated_fields.append("venue_type")
                else:
                    unchanged_fields.append(param)
            case _:
                current_value = getattr(event, param)
                new_value = data[param]

                if current_value != new_value:
                    setattr(event, param, new_value)
                    updated_fields.append(param)

                    # Update slug if English name or start_date changes
                    if param in ["name_en", "start_date"]:
                        # date format for slug
                        slug_date = data.get('start_date', event.start_date).strftime('%Y-%m-%d-%H-%M')
                        event.slug = slugify(f"{event.name_en}-{slug_date}")
                        if "slug" not in updated_fields:
                            updated_fields.append("slug")
                else:
                    unchanged_fields.append(param)

    if updated_fields:
        event.save()
        event.reload()  # correct time (while saving it is in our timezone but stores in utc)
        message = f"Updated fields: {', '.join(updated_fields)}"
        if unchanged_fields:
            message += f". Unchanged fields: {', '.join(unchanged_fields)}"
    else:
        message = "No fields were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": event.to_response_dict()
    }), 200


def delete_existing_event(slug):
    """

    """

    # Find existing event
    event = Event.objects(slug=slug).first()
    if not event:
        raise UserError(f"Event with slug '{slug}' not found", 404)

    # delete the event and image from image_path
    delete_folder_from_path(event.image_path)
    event.delete()

    # Return 204 No Content for successful deletion
    return '', 204
