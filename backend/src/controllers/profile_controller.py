from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from backend.src.models.user import User
from backend.src.utils.constants import ALLOWED_PROFILE_BODY_PARAMS
from backend.src.utils.exceptions import UserError
from backend.src.utils.pre_mongo_validators import validate_user_data
from backend.src.models.event import Event


def get_user_profile():
    """

    """
    # getting user id from jwt
    current_user_id = get_jwt_identity()

    # Get user
    user = User.objects(id=current_user_id).first()
    if not user:
        raise UserError(f"User with id {current_user_id} not found", 404)

    # Format response data
    user_data = user.to_profile_response_dict()

    return jsonify({
        "status": "success",
        "data": user_data
    }), 200


def full_update_user_profile():
    """

    """
    data = request.get_json()

    # getting user id from jwt
    current_user_id = get_jwt_identity()

    # Get user
    user = User.objects(id=current_user_id).first()
    if not user:
        raise UserError(f"User with id {current_user_id} not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_PROFILE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = ALLOWED_PROFILE_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    validate_user_data(data)  # pre-mongo validation

    # update user with data
    user.email = data['email']
    user.password = data['password']  # clean from model is responsible for hashing
    user.default_lang = data['default_lang']

    user.save()

    return jsonify({
        'status': 'success',
        'message': "User's profile fully updated successfully",
        "data": user.to_profile_response_dict()
    }), 200


def part_update_user_profile():
    """

    """
    data = request.get_json()

    # getting user id from jwt
    current_user_id = get_jwt_identity()

    # Get user
    user = User.objects(id=current_user_id).first()
    if not user:
        raise UserError(f"User with id {current_user_id} not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_PROFILE_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    validate_user_data(data)  # pre-mongo validation

    # Track changes
    updated_params = []
    unchanged_params = []

    for param, value in data.items():
        if param == 'password':  # check if new password is different from stored in hash
            if user.verify_password(value):
                unchanged_params.append(param)
            else:
                setattr(user, param, value)
                updated_params.append(param)
        else:
            current_value = getattr(user, param)

            if current_value != value:
                setattr(user, param, value)
                updated_params.append(param)
            else:
                unchanged_params.append(param)

    if updated_params:
        user.save()
        message = f"Updated parameters: {', '.join(updated_params)}"
        if unchanged_params:
            message += f". Unchanged parameters: {', '.join(unchanged_params)}"
    else:
        message = "No parameters were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": user.to_profile_response_dict()
    }), 200


def add_event_to_favorites(event_slug):
    """

    """
    current_user_id = get_jwt_identity()

    # Get user and event
    user = User.objects(id=current_user_id).first()
    if not user:
        raise UserError(f"User with id {current_user_id} not found", 404)

    event = Event.objects(slug=event_slug).first()
    if not event:
        raise UserError(f"Event with slug '{event_slug}' not found", 404)

    # Check if event is already in favorites
    if event in user.favorite_events:
        return jsonify({
            "status": "success",
            "message": "Event already in favorites",
            "data": user.to_profile_response_dict()
        }), 200

    # Add to favorites
    User.objects(id=current_user_id).update_one(add_to_set__favorite_events=event)
    user.reload()

    return jsonify({
        "status": "success",
        "message": "Event added to favorites",
        "data": user.to_profile_response_dict()
    }), 200


def remove_event_from_favorites(event_slug):
    """

    """
    # getting user id from jwt
    current_user_id = get_jwt_identity()

    # Get user and event
    user = User.objects(id=current_user_id).first()
    if not user:
        raise UserError(f"User with id {current_user_id} not found", 404)

    event = Event.objects(slug=event_slug).first()
    if not event:
        raise UserError(f"Event with slug '{event_slug}' not found", 404)

    # Check if event is in favorites
    if event not in user.favorite_events:
        return jsonify({
            "status": "success",
            "message": "Event not in favorites",
            "data": user.to_profile_response_dict()
        }), 200

    # Remove from favorites
    User.objects(id=current_user_id).update_one(pull__favorite_events=event)
    user.reload()

    return jsonify({
        "status": "success",
        "message": "Event removed from favorites",
        "data": user.to_profile_response_dict()
    }), 200
