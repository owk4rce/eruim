from flask import Blueprint, jsonify, request
from slugify import slugify
from backend.src.models.event_type import EventType
from werkzeug.exceptions import BadRequest
from mongoengine.errors import ValidationError, NotUniqueError
from backend.src.utils.language_utils import validate_language

# Create Blueprint for event types
event_types_bp = Blueprint("event_types", __name__, url_prefix="/event_types")


@event_types_bp.route("/", methods=["GET"])
def get_event_types():
    """
    Get list of all event types

    Query Parameters:
        - lang (str, optional): Language for event types (en, ru, he). Defaults to 'en'

    Returns:
        JSON response with:
        - status: success/error
        - data: list of event types or error message
    """
    try:
        # Get language preference from query parameter, default to English
        lang_arg = request.args.get("lang", "en")
        language = validate_language(lang_arg)
        if language is None:
            return jsonify({
                'status': 'error',
                'message': f'Unsupported language: {lang_arg}'
            }), 400

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

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@event_types_bp.route("/", methods=["POST"])
def add_event_type():
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 415

        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Body parameters are missing."
            }), 400

        if len(data) != 3:
            return jsonify({
                "status": "error",
                "message": "Incorrect number of parameters in body."
            }), 400

        if "name_en" not in data:
            return jsonify({
                "status": "error",
                "message": "Parameter 'name_en' is missing."
            }), 400

        if "name_ru" not in data:
            return jsonify({
                "status": "error",
                "message": "Parameter 'name_ru' is missing."
            }), 400

        if "name_he" not in data:
            return jsonify({
                "status": "error",
                "message": "Parameter 'name_he' is missing."
            }), 400

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

    except BadRequest:  # Empty or invalid JSON
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format or empty request body.'
        }), 400

    except ValidationError as e:  # MongoEngine validation errors (regex, min_length, etc.)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


    except NotUniqueError:  # Duplicate key error
        return jsonify({
            'status': 'error',
            'message': 'City with this name already exists'
        }), 409


    except Exception as e:  # Unexpected errors
        print(f"Error in add_event_type: {str(e)}")  # log for debugging
        return jsonify({
            'status': 'error',
            'message': 'Internal Server Error'
        }), 500
