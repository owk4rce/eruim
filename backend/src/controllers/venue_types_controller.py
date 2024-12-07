from flask import request, jsonify
from slugify import slugify

from backend.src.models.venue import Venue
from backend.src.models.venue_type import VenueType
from backend.src.services.translation_service import translate_with_google
from backend.src.utils.constants import ALLOWED_VENUE_TYPE_BODY_PARAMS, SUPPORTED_LANGUAGES
from backend.src.utils.exceptions import UserError
from backend.src.utils.pre_mongo_validators import validate_venue_type_data

import logging
logger = logging.getLogger('backend')


def get_all_venue_types():
    """
    Get list of all venue types.

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

    # Get all venue types from database
    venue_types = VenueType.objects()
    # Format response data using the requested language
    venue_types_data = [venue_type.to_response_dict(lang_arg) for venue_type in venue_types]

    return jsonify({
        "status": "success",
        "data": venue_types_data,
        "count": len(venue_types_data)
    }), 200


def get_existing_venue_type(slug):
    """
    Get single venue type by slug.

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
    Create new venue type with auto-translation.

    Expected body:
        At least one name in any supported language:
        {
            "name_en": "museum" and/or
            "name_ru": "музей" and/or
            "name_he": "מוזיאון"
        }

    Process:
        1. Validates provided name
        2. Auto-translates to other languages
        3. Creates venue type with slug from English name
    """
    data = request.get_json()

    unknown_params = set(data.keys()) - ALLOWED_VENUE_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    if "name_en" in data:
        data["name_en"] = data["name_en"].lower()   # not punishing managers for uppercase in body

    if "name_ru" in data:
        data["name_ru"] = data["name_ru"].lower()

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

    logger.info(f"Created new venue type: {name_en}")

    return jsonify({
        "status": "success",
        "message": "Venue type created successfully",
        "data": venue_type.to_response_dict()
    }), 201


def full_update_existing_venue_type(slug):
    """
    Full update of venue type.

    Expected body:
        {
            "name_en": "museum",
            "name_ru": "музей",
            "name_he": "מוזיאון"
        }
    """
    data = request.get_json()

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

    data["name_en"] = data["name_en"].lower()  # not punishing managers for uppercase in body
    data["name_ru"] = data["name_ru"].lower()

    validate_venue_type_data(data)  # pre-mongo validation

    update_data = {
        "set__name_en": data["name_en"],
        "set__name_ru": data["name_ru"],
        "set__name_he": data["name_he"],
        "set__slug": slugify(data["name_en"])
    }

    # atomic update
    VenueType.objects(slug=slug).update_one(**update_data)

    # reload to get new for response
    venue_type.reload()

    logger.info(f"Full update of venue type: {data['name_en']}")

    return jsonify({
        "status": "success",
        "message": "Venue type fully updated successfully.",
        "data": venue_type.to_response_dict()
    }), 200


def part_update_existing_venue_type(slug):
    """
    Partial update of venue type.

    Expected body:
        One or more names to update:
        {
            "name_en": "museum" and/or
            "name_ru": "музей" and/or
            "name_he": "מוזיאון"
        }
    """
    data = request.get_json()

    # Find existing venue type
    venue_type = VenueType.objects(slug=slug).first()
    if not venue_type:
        raise UserError(f"Venue type with slug '{slug}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_VENUE_TYPE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    if "name_en" in data:   # not punishing managers for uppercase in body
        data["name_en"] = data["name_en"].lower()

    if "name_ru" in data:
        data["name_ru"] = data["name_ru"].lower()

    validate_venue_type_data(data)  # pre-mongo validation

    # Track changes
    update_data = {}
    unchanged_params = []

    for param, value in data.items():
        current_value = getattr(venue_type, param)

        if current_value != value:
            update_data[f"set__{param}"] = value

            # Update slug if English name changes
            if param == "name_en":
                update_data["set__slug"] = slugify(value)
        else:
            unchanged_params.append(param)

    if update_data:
        VenueType.objects(slug=slug).update_one(**update_data)
        venue_type.reload()
        updated_params = [param.replace('set__', '') for param in update_data.keys()]
        logger.info(f"Partial update of venue type {venue_type.name_en}, fields: {', '.join(updated_params)}")
        message = f"Updated parameters: {', '.join(updated_params)}"
        if unchanged_params:
            message += f". Unchanged parameters: {', '.join(unchanged_params)}"
    else:
        message = "No parameters were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": venue_type.to_response_dict()
    }), 200


def delete_existing_venue_type(slug):
    """
    Delete venue type if no associated venues exist.
    """
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
    logger.info(f"Deleting venue type: {venue_type.name_en}")
    venue_type.delete()

    # Return 204 No Content for successful deletion
    return '', 204
