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
    if request.data:
        raise UserError("Using body in GET-method is restricted.")

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
        "data": event_types_data
    }), 200


def get_existing_event_type(slug):
    """

    """
    if request.data:
        raise UserError("Using body in GET-method is restricted.")

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
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    unknown_params = set(data.keys()) - ALLOWED_EVENT_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

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
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

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

    validate_event_type_data(data)  # pre-mongo validation

    event_type.name_en = data["name_en"]
    event_type.name_he = data["name_he"]
    event_type.name_ru = data["name_ru"]
    event_type.slug = slugify(data["name_en"])

    event_type.save()

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
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    # Find existing event type
    event_type = EventType.objects(slug=slug).first()
    if not event_type:
        raise UserError(f"Event type with slug '{slug}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_EVENT_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    validate_event_type_data(data)  # pre-mongo validation

    # Track changes
    updated_fields = []
    unchanged_fields = []

    for param in data:
        current_value = getattr(event_type, param)
        new_value = data[param]

        if current_value != new_value:
            setattr(event_type, param, new_value)
            updated_fields.append(param)

            # Update slug if English name changes
            if param == "name_en":
                event_type.slug = slugify(new_value)
                updated_fields.append("slug")
        else:
            unchanged_fields.append(param)

    if updated_fields:
        event_type.save()
        message = f"Updated fields: {', '.join(updated_fields)}"
        if unchanged_fields:
            message += f". Unchanged fields: {', '.join(unchanged_fields)}"
    else:
        message = "No fields were updated as all values are the same."

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
    if request.data:
        raise UserError("Using body in DELETE-method is restricted.")

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
