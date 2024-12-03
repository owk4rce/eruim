from flask import request, jsonify
from backend.src.models.user import User
from backend.src.utils.constants import ALLOWED_USER_BODY_PARAMS, REQUIRED_USER_BODY_PARAMS
from backend.src.utils.exceptions import UserError
from backend.src.utils.pre_mongo_validators import validate_user_data


def get_all_users():
    """

    """
    if request.data:
        raise UserError("Using body in GET-method is restricted.")

    unknown_args = set(request.args.keys()) - {"is_active", "role"}
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    # Start with base query
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

    # Add role filter if provided
    role_arg = request.args.get("role")
    if role_arg:
        if role_arg not in ['admin', 'manager', 'user']:
            raise UserError("Invalid role. Must be one of: 'admin', 'manager', 'user'")
        query["role"] = role_arg

    # Get users from database with filters
    users = User.objects(**query)

    # Format response
    users_data = [user.to_response_dict() for user in users]

    return jsonify({
        "status": "success",
        "data": users_data,
        "count": len(users_data)
    }), 200


def get_existing_user(user_id):
    """

    """
    if request.data:
        raise UserError("Using body in GET-method is restricted.")

    if request.args:
        raise UserError(f"Arguments in this request are restricted.")

    # Get one user from database
    user = User.objects(id=user_id).first()

    if not user:
        raise UserError(f"User with id '{user_id}' not found", 404)

    # Format response data
    user_data = user.to_response_dict()

    return jsonify({
        "status": "success",
        "data": user_data
    }), 200


def create_new_user():
    """

    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    unknown_params = set(data.keys()) - ALLOWED_USER_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = REQUIRED_USER_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    validate_user_data(data)  # pre-mongo validation

    # Create user with data
    user = User(
        email=data['email'],
        password=data['password'],  # clean from model is responsible for hashing
        role=data['role'],
        is_active=data.get('is_active', True),
        default_lang=data.get('default_lang', 'en')
    )
    user.save()

    return jsonify({
        'status': 'success',
        'message': 'User created successfully',
        "data": user.to_response_dict()
    }), 201


def full_update_existing_user(user_id):
    """

    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    # Find existing user
    user = User.objects(id=user_id).first()
    if not user:
        raise UserError(f"User with id '{user_id}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_USER_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = ALLOWED_USER_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    validate_user_data(data)  # pre-mongo validation

    # Fully update user with data
    user.email=data['email']
    user.password=data['password']  # clean from model is responsible for hashing
    user.role=data['role']
    user.is_active=data['is_active']
    user.default_lang=data['default_lang']

    user.save()

    return jsonify({
        'status': 'success',
        'message': 'User fully updated successfully',
        "data": user.to_response_dict()
    }), 200


def part_update_existing_user(user_id):
    """

    """
    if not request.is_json:
        raise UserError("Content-Type must be application/json.", 415)

    data = request.get_json()
    if not data:
        raise UserError("Body parameters are missing.")

    # Find existing user
    user = User.objects(id=user_id).first()
    if not user:
        raise UserError(f"User with id '{user_id}' not found", 404)

    unknown_params = set(data.keys()) - ALLOWED_USER_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    validate_user_data(data)  # pre-mongo validation

    # Track changes
    updated_fields = []
    unchanged_fields = []

    for param in data:
        if param == 'password':     # check if new password is different from stored in hash
            if user.verify_password(data['password']):
                unchanged_fields.append(param)
            else:
                setattr(user, param, data['password'])
                updated_fields.append(param)
        else:
            current_value = getattr(user, param)
            new_value = data[param]

            if current_value != new_value:
                setattr(user, param, new_value)
                updated_fields.append(param)
            else:
                unchanged_fields.append(param)

    if updated_fields:
        user.save()
        message = f"Updated fields: {', '.join(updated_fields)}"
        if unchanged_fields:
            message += f". Unchanged fields: {', '.join(unchanged_fields)}"
    else:
        message = "No fields were updated as all values are the same."

    return jsonify({
        "status": "success",
        "message": message,
        "data": user.to_response_dict()
    }), 200


def delete_existing_user(user_id):
    """

    """
    if request.data:
        raise UserError("Using body in DELETE-method is restricted.")

    # Find existing user
    user = User.objects(id=user_id).first()
    if not user:
        raise UserError(f"User with id '{user_id}' not found", 404)

    user.delete()

    # Return 204 No Content for successful deletion
    return '', 204
