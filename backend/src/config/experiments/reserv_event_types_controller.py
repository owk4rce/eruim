from flask import request, jsonify
from slugify import slugify
from backend.src.utils.constants import REQUIRED_EVENT_TYPE_BODY_PARAMS
from backend.src.utils.exceptions import UserError
from backend.src.config.experiments.language_utils import validate_language
from backend.src.models.event_type import EventType


def get_all_event_types():
    """
    Get list of all event types

    Query Parameters:
        - lang (str, optional): Language for event types (en, ru, he). Defaults to 'en'

    Returns:
        JSON response with:
        - status: success/error
        - data: list of event types or error message
    """
    if request.data:
        raise UserError("Using body in GET-method is restricted.")

    # Get language preference from query parameter, default to English
    lang_arg = request.args.get("lang", "en")
    language = validate_language(lang_arg)
    if language is None:
        raise UserError(f"Unsupported language: {lang_arg}")

    # Get all event types from database
    event_types = EventType.objects()
    # Format response data using the requested language
    event_types_data = [{
        "name": event_type.get_name(language),
        "slug": event_type.slug
    } for event_type in event_types]

    return jsonify({
        "status": "success",
        "data": event_types_data
    }), 200


def create_new_event_type():
    """
    Create new event type

    Query Body Parameters:
        - name_en (str, required): Name in English
        - name_ru (str, required): Name in Russian
        - name_he (str, required): Name in Hebrew

    Returns:
        JSON response with:
        - status: success/error
        - message: new event type created
    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    if len(data) != 3:
        raise UserError("Incorrect number of parameters in body.")

    for param in REQUIRED_EVENT_TYPE_BODY_PARAMS:
        if param not in data:
            raise UserError(f"Body parameter '{param}' is missing")
        elif not isinstance(data[param], str):
            raise UserError(f"Body parameter {param} must be a string")

    event_type = EventType(name_en=data["name_en"],
                           name_ru=data["name_ru"],
                           name_he=data["name_he"],
                           slug=slugify(data["name_en"])
                           )
    event_type.save()

    return jsonify({
        "status": "success",
        "message": "Event type created successfully"
    }), 201

