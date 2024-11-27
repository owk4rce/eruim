from flask import request, jsonify
from backend.src.models.venue import Venue
from backend.src.utils.language_utils import validate_language


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
    try:
        if request.data:
            return jsonify({
                "status": "error",
                "message": "Using body in GET-method is restricted."
            }), 400

        # Get language preference from query parameter, default to English
        lang_arg = request.args.get("lang", "en")
        language = validate_language(lang_arg)
        if language is None:
            return jsonify({
                "status": "error",
                "message": f"Unsupported language: {lang_arg}"
            }), 400

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

        # Format response data using the requested language
        venues_data = [{
            "name": venue.get_name(language),
            "address": venue.get_address(language),
            "description": venue.get_description(language),
            "city": {
                "name": venue.city.get_name(language),
                "slug": venue.city.slug
            },
            "location": venue.location,
            "website": venue.website,
            "phone": venue.phone,
            "email": venue.email,
            "is_active": venue.is_active,
            "slug": venue.slug
        } for venue in venues]

        return jsonify({
            'status': 'success',
            'data': venues_data,
            'count': len(venues_data)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
