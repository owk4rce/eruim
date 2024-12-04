from flask import request, jsonify
from slugify import slugify
from backend.src.models.venue import Venue
from backend.src.models.venue_type import VenueType
from backend.src.services.translation_service import translate_with_google
from backend.src.utils.constants import ALLOWED_VENUE_TYPE_BODY_PARAMS, SUPPORTED_LANGUAGES
from backend.src.utils.exceptions import UserError
from backend.src.utils.pre_mongo_validators import validate_venue_type_data


def get_all_venue_types():
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

    # Get all venue types from database
    venue_types = VenueType.objects()
    # Format response data using the requested language
    venue_types_data = [venue_type.to_response_dict(lang_arg) for venue_type in venue_types]

    return jsonify({
        "status": "success",
        "data": venue_types_data
    }), 200


def get_existing_venue_type(slug):
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

    # Get one venue type from database
    venue_type = VenueType.objects(slug=slug).first()

    if not venue_type:
        raise UserError(f"Venue type with slug {slug} not found", 404)

    # Format response data using the requested language
    venue_type_data = venue_type.to_response_dict(lang_arg)

    return jsonify({
        "status": "success",
        "data": venue_type_data
    }), 200


def create_new_venue_type():
    """
    Create new venue type with automatic translation of missing names.

    Request Body:
        JSON object with at least one name field (required):
        - name_en (str, optional): Name in English
        - name_ru (str, optional): Name in Russian
        - name_he (str, optional): Name in Hebrew

        Example (minimum valid request):
            {
                "name_en": "Concert"
            }
            or
            {
                "name_ru": "Концерт"
            }
            or
            {
                "name_he": "קונצרט"
            }

        Missing names will be auto-translated from the provided one.

    Returns:
        tuple: (JSON response, status code)
            - response format:
                {
                    "status": "success",
                    "message": str
                }
            - status codes:
                201: created successfully
                400: validation error (missing all name fields/wrong format)
                415: wrong content type
    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    unknown_params = set(data.keys()) - ALLOWED_VENUE_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    validate_venue_type_data(data)  # pre-mongo validation

    if "name_en" in data:
        # Check if 'name_en' already in use
        if VenueType.objects(name_en=data["name_en"]).first():
            raise UserError(f"Venue type with name '{data['name_en']}' already exists", 409)
        source_lang = "en"
        source_text = data["name_en"]
    elif "name_he" in data:
        # Check if 'name_he' already in use
        if VenueType.objects(name_he=data["name_he"]).first():
            raise UserError(f"Venue type with name '{data['name_he']}' already exists", 409)
        source_lang = "iw"  # Google Translate uses 'iw'
        source_text = data["name_he"]
    elif "name_ru" in data:
        # Check if 'name_ru' already in use
        if VenueType.objects(name_ru=data["name_ru"]).first():
            raise UserError(f"Venue type with name '{data['name_ru']}' already exists", 409)
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

    venue_type = VenueType(name_en=name_en,
                           name_ru=name_ru,
                           name_he=name_he,
                           slug=slugify(name_en)
                           )
    venue_type.save()

    return jsonify({
        "status": "success",
        "message": "Venue type created successfully",
        "data": venue_type.to_response_dict()
    }), 201


def full_update_existing_venue_type(slug):
    """
    Update existing venue type

    Query Body Parameters:
        - name_en (str, required): Name in English
        - name_ru (str, required): Name in Russian
        - name_he (str, required): Name in Hebrew

    Returns:
        JSON response with:
        - status: success/error
        - message: venue type updated
    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    # Find existing venue type
    venue_type = VenueType.objects(slug=slug).first()
    if not venue_type:
        raise UserError(f"Venue type with slug '{slug}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_VENUE_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = ALLOWED_VENUE_TYPE_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    validate_venue_type_data(data)  # pre-mongo validation

    venue_type.name_en = data["name_en"]
    venue_type.name_he = data["name_he"]
    venue_type.name_ru = data["name_ru"]
    venue_type.slug = slugify(data["name_en"])

    venue_type.save()

    return jsonify({
        "status": "success",
        "message": "Venue type fully updated successfully.",
        "data": venue_type.to_response_dict()
    }), 200


def part_update_existing_venue_type(slug):
    """
    Partial update existing venue type

    Query Body Parameters:
        - name_en (str, optional): Name in English
        - name_ru (str, optional): Name in Russian
        - name_he (str, optional): Name in Hebrew

    Returns:
        JSON response with:
        - status: success/error
        - message: venue type updated
    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    # Find existing venue type
    venue_type = VenueType.objects(slug=slug).first()
    if not venue_type:
        raise UserError(f"Venue type with slug '{slug}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_VENUE_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    validate_venue_type_data(data)  # pre-mongo validation

    # Track changes
    updated_fields = []
    unchanged_fields = []

    for param in data:
        current_value = getattr(venue_type, param)
        new_value = data[param]

        if current_value != new_value:
            setattr(venue_type, param, new_value)
            updated_fields.append(param)

            # Update slug if English name changes
            if param == "name_en":
                venue_type.slug = slugify(new_value)
                updated_fields.append("slug")
        else:
            unchanged_fields.append(param)

    if updated_fields:
        venue_type.save()
        message = f"Updated fields: {', '.join(updated_fields)}"
        if unchanged_fields:
            message += f". Unchanged fields: {', '.join(unchanged_fields)}"
    else:
        message = "No fields were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": venue_type.to_response_dict()
    }), 200


def delete_existing_venue_type(slug):
    """
    Delete existing venue type if there are no venues with this type

    Returns:
        JSON response with:
        - status: error
        - message: venue type updated

        204
    """
    if request.data:
        raise UserError("Using body in DELETE-method is restricted.")

    # Find existing venue type
    venue_type = VenueType.objects(slug=slug).first()
    if not venue_type:
        raise UserError(f"Venue type with slug '{slug}' not found", 404)

    associated_venues = Venue.objects(venue_type=venue_type).count()

    if associated_venues > 0:
        raise UserError(
            "Cannot delete this venue type. Please delete all associated venues first.",
            409
        )

    # If no associated venues, delete the venue type
    venue_type.delete()

    # Return 204 No Content for successful deletion
    return '', 204
