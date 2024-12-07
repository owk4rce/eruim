from flask import request, jsonify
from slugify import slugify

from backend.src.services.translation_service import translate_with_google
from backend.src.utils.constants import ALLOWED_EVENT_TYPE_BODY_PARAMS, SUPPORTED_LANGUAGES
from backend.src.utils.exceptions import UserError
from backend.src.models.event_type import EventType
from backend.src.models.event import Event
from backend.src.utils.pre_mongo_validators import validate_event_type_data


def get_all_event_types():
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

    # Get all event types from database
    event_types = EventType.objects()
    # Format response data using the requested language
    event_types_data = [event_type.to_response_dict(lang_arg) for event_type in event_types]

    return jsonify({
        "status": "success",
        "data": event_types_data,
        "count": EventType.objects.count()
    }), 200


def get_existing_event_type(slug):
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

    # Get one event type from database
    venue_type = EventType.objects(slug=slug).first()

    if not venue_type:
        raise UserError(f"Event type with slug {slug} not found", 404)

    # Format response data using the requested language
    venue_type_data = venue_type.to_response_dict(lang_arg)

    return jsonify({
        "status": "success",
        "data": venue_type_data
    }), 200


def create_new_event_type():
    """

    """
    data = request.get_json()

    unknown_params = set(data.keys()) - ALLOWED_EVENT_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    if "name_en" in data:
        data["name_en"] = data["name_en"].lower()   # not punishing managers for uppercase in body

    if "name_ru" in data:
        data["name_ru"] = data["name_ru"].lower()

    validate_event_type_data(data)  # pre-mongo validation

    if "name_en" in data:
        # Check if 'name_en' already in use
        if EventType.objects(name_en=data["name_en"]).first():
            raise UserError(f"Event type with name '{data['name_en']}' already exists", 409)
        source_lang = "en"
        source_text = data["name_en"]
    elif "name_he" in data:
        # Check if 'name_he' already in use
        if EventType.objects(name_he=data["name_he"]).first():
            raise UserError(f"Event type with name '{data['name_he']}' already exists", 409)
        source_lang = "iw"  # Google Translate uses 'iw'
        source_text = data["name_he"]
    elif "name_ru" in data:
        # Check if 'name_ru' already in use
        if EventType.objects(name_ru=data["name_ru"]).first():
            raise UserError(f"Event type with name '{data['name_ru']}' already exists", 409)
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

    event_type = EventType(name_en=name_en,
                           name_ru=name_ru,
                           name_he=name_he,
                           slug=slugify(name_en)
                           )
    event_type.save()

    return jsonify({
        "status": "success",
        "message": "Event type created successfully",
        "data": event_type.to_response_dict()
    }), 201


def full_update_existing_event_type(slug):
    """
    Update existing event type

    Query Body Parameters:
        - name_en (str, required): Name in English
        - name_ru (str, required): Name in Russian
        - name_he (str, required): Name in Hebrew

    Returns:
        JSON response with:
        - status: success/error
        - message: event type updated
    """
    data = request.get_json()

    # Find existing event type
    event_type = EventType.objects(slug=slug).first()
    if not event_type:
        raise UserError(f"Event type with slug '{slug}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_EVENT_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = ALLOWED_EVENT_TYPE_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    data["name_en"] = data["name_en"].lower()   # not punishing managers for uppercase in body
    data["name_ru"] = data["name_ru"].lower()

    validate_event_type_data(data)  # pre-mongo validation

    update_data = {
        "set__name_en": data["name_en"],
        "set__name_ru": data["name_ru"],
        "set__name_he": data["name_he"],
        "set__slug": slugify(data["name_en"])
    }

    # atomic update
    EventType.objects(slug=slug).update_one(**update_data)

    # reload to get new for response
    event_type.reload()

    return jsonify({
        "status": "success",
        "message": "Event type fully updated successfully.",
        "data": event_type.to_response_dict()
    }), 200


def part_update_existing_event_type(slug):
    """
    Partial update existing event type

    Query Body Parameters:
        - name_en (str, optional): Name in English
        - name_ru (str, optional): Name in Russian
        - name_he (str, optional): Name in Hebrew

    Returns:
        JSON response with:
        - status: success/error
        - message: event type updated
    """
    data = request.get_json()

    # Find existing event type
    event_type = EventType.objects(slug=slug).first()
    if not event_type:
        raise UserError(f"Event type with slug '{slug}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_EVENT_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    if "name_en" in data:   # not punishing managers for uppercase in body
        data["name_en"] = data["name_en"].lower()

    if "name_ru" in data:
        data["name_ru"] = data["name_ru"].lower()

    validate_event_type_data(data)  # pre-mongo validation

    # Track changes
    update_data = {}
    unchanged_params = []

    for param, value in data.items():
        current_value = getattr(event_type, param)

        if current_value != value:
            update_data[f"set__{param}"] = value

            # Update slug if English name changes
            if param == "name_en":
                update_data["set__slug"] = slugify(value)
        else:
            unchanged_params.append(param)

    if update_data:
        EventType.objects(slug=slug).update_one(**update_data)
        event_type.reload()
        updated_params = [param.replace('set__', '') for param in update_data.keys()]
        message = f"Updated parameters: {', '.join(updated_params)}"
        if unchanged_params:
            message += f". Unchanged parameters: {', '.join(unchanged_params)}"
    else:
        message = "No parameters were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": event_type.to_response_dict()
    }), 200


def delete_existing_event_type(slug):
    """
    Delete existing event type if there are no events with this type

    Returns:
        JSON response with:
        - status: error
        - message: event type updated

        204
    """
    # Find existing event type
    event_type = EventType.objects(slug=slug).first()
    if not event_type:
        raise UserError(f"Event type with slug '{slug}' not found", 404)

    associated_events = Event.objects(event_type=event_type).count()

    if associated_events > 0:
        raise UserError(
            "Cannot delete this event type. Please delete all associated events first.",
            409
        )

    # If no associated events, delete the event type
    event_type.delete()

    # Return 204 No Content for successful deletion
    return '', 204
