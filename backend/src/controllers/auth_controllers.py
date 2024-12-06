from backend.src.models.user import User
from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token
from datetime import datetime

from backend.src.utils.constants import ALLOWED_AUTH_BODY_PARAMS, REQUIRED_AUTH_BODY_PARAMS
from backend.src.utils.exceptions import UserError
from backend.src.utils.pre_mongo_validators import validate_user_data


def register_new_user():
    data = request.get_json()

    unknown_params = set(data.keys()) - ALLOWED_AUTH_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = REQUIRED_AUTH_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    validate_user_data(data)  # pre-mongo validation

    # Check if email already exists
    if User.objects(email=data['email']).first():
        raise UserError("User with this email already exists.", 409)

    # Create user
    user = User(
        email=data['email'],
        password=data['password'],
        role='user',  # всегда user при регистрации
        is_active=True,  # всегда активный при регистрации
        default_lang=data.get('default_lang', 'en')
    )
    user.save()

    # Create access token
    access_token = create_access_token(identity=str(user.id))

    # Create response
    response = jsonify({
        'status': 'success',
        'message': 'Registration successful.',
        'data': user.to_response_dict()
    })

    # Set token in cookie
    response.set_cookie(
        "token",
        access_token,
        httponly=True,  # js read token restricted
        secure=current_app.config["JWT_COOKIE_SECURE"],
        samesite="Strict",  # defend from CSRF
        max_age=24 * 60 * 60  # same as token life - 1 day
    )

    return response, 201


def existing_user_login():
    data = request.get_json()

    unknown_params = set(data.keys()) - REQUIRED_AUTH_BODY_PARAMS
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    missing_params = REQUIRED_AUTH_BODY_PARAMS - set(data.keys())
    if missing_params:
        raise UserError(f"Required body parameters are missing: {', '.join(missing_params)}")

    # Find user by email
    user = User.objects(email=data["email"]).first()
    if not user:
        raise UserError("Invalid email or password.", 401)

    # Verify password
    if not user.verify_password(data["password"]):
        raise UserError("Invalid email or password.", 401)

    # Check if user is active
    if not user.is_active:
        raise UserError("Account is inactive.", 403)

    # Create access token
    access_token = create_access_token(identity=str(user.id))

    # Update last login time
    user.last_login = datetime.utcnow()
    user.save()

    # Create response
    response = jsonify({
        "status": "success",
        "message": "Login successful.",
        "data": user.to_response_dict()
    })

    # Set token in cookie
    response.set_cookie(
        "token",
        access_token,
        httponly=True,
        secure=current_app.config["JWT_COOKIE_SECURE"],
        samesite='Strict',
        max_age=24 * 60 * 60    # same as token life - 1 day
    )

    return response, 200


def user_logout():
    """
    Logout user by removing JWT token cookie

    Returns:
        Success message
    """
    response = jsonify({
        'status': 'success',
        'message': 'Logout successful.'
    })

    # Remove token cookie
    response.delete_cookie(
        'token',
        httponly=True,
        secure=current_app.config["JWT_COOKIE_SECURE"],
        samesite='Strict'
    )

    return response, 200
