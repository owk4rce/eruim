import re
from backend.src.models.user import User
from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token
from datetime import datetime

from backend.src.utils.constants import ALLOWED_AUTH_BODY_PARAMS, REQUIRED_AUTH_BODY_PARAMS, USER_PATTERNS
from backend.src.utils.email_utils import send_reset_password_email, send_account_activation_email
from backend.src.utils.exceptions import UserError
from backend.src.utils.pre_mongo_validators import validate_user_data
import logging

from backend.src.utils.temp_token import generate_service_token

logger = logging.getLogger('backend')


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
        is_active=False,  # всегда активный при регистрации
        default_lang=data.get('default_lang', 'en')
    )
    user.save()

    # Create access token
    access_token = create_access_token(identity=str(user.id))

    #
    # Generate and save reset token
    activation_token = generate_service_token()
    user.set_email_confirmation_token(activation_token)

    # Create activation link
    base_url = current_app.config.get("BASE_URL", "http://localhost:5000")
    activation_link = f"{base_url}/api/v1/auth/confirm_email/verify?token={activation_token}"

    send_account_activation_email(user.email, activation_link)
    #

    # Create response
    response = jsonify({
        'status': 'success',
        'message': 'Registration successful. The activation email sent.',
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
        max_age=24 * 60 * 60  # same as token life - 1 day
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


def request_password_reset():
    """
    Handle password reset request

    Expected body: {"email": "user@example.com"}
    Returns success message regardless of whether email exists (security)
    """
    data = request.get_json()

    unknown_params = set(data.keys()) - {"email"}
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    if "email" not in data:
        raise UserError("Email is required.")

    # for security reason we are not telling if the email exists in our db
    universal_response = {
        "status": "success",
        "message": "If the email exists, reset instructions will be sent."
    }

    # Find user by email
    user = User.objects(email=data["email"]).first()

    # If user not found, still return success (prevents email enumeration)
    if not user:
        logger.info(f"Password reset requested for non-existent email: {data['email']}")
        return jsonify(universal_response), 200

    # Generate and save reset token
    reset_token = generate_service_token()
    user.set_reset_password_token(reset_token)

    # Create reset link
    base_url = current_app.config.get("BASE_URL", "http://localhost:5000")
    reset_link = f"{base_url}/api/v1/auth/reset-password/verify?token={reset_token}"

    send_reset_password_email(user.email, reset_link)
    logger.info(f"Password reset link sent to: {user.email}")

    return jsonify(universal_response), 200


def verify_reset_token():
    """
    Verify reset password token validity

    Expected args: ?token=xxx
    Returns: success if token is valid and not expired
    """
    unknown_args = set(request.args.keys()) - {"token"}
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    token = request.args.get('token')
    if not token:
        raise UserError("Reset token is required.")

    user = User.objects(reset_password_token=token).first()
    if not user or not user.is_reset_token_valid(token):
        raise UserError("Invalid or expired reset token.")

    return jsonify({
        "status": "success",
        "message": "Token is valid."
    }), 200


def confirm_password_reset():
    """
    Set new password using reset token

    Expected body: {
        "token": "xxx",
        "new_password": "newpass123"
    }
    """
    data = request.get_json()

    unknown_params = set(data.keys()) - {"token", "new_password"}
    if unknown_params:
        raise UserError(f"Unknown parameters in request: {', '.join(unknown_params)}")

    if "token" not in data or "new_password" not in data:
        raise UserError("Token and new password are required.")

    if not re.match(USER_PATTERNS["password"], data["new_password"]):
        raise UserError(
            'Password requirements: '
            'At least 8 characters long. '
            'Only English letters (a-z, A-Z). '
            'At least one uppercase letter. '
            'At least one lowercase letter. '
            'At least one number. '
            'At least one special character (@$!%*?&).'
        )

    user = User.objects(reset_password_token=data["token"]).first()
    if not user or not user.is_reset_token_valid(data["token"]):
        raise UserError("Invalid or expired reset token.")

    user.password = data["new_password"]
    user.clear_reset_password_token()  # clear token after use
    user.save()

    return jsonify({
        "status": "success",
        "message": "Password has been reset successfully."
    }), 200


def verify_email_confirmation_token():
    """
    Verify token from activation email
    """
    unknown_args = set(request.args.keys()) - {"token"}
    if unknown_args:
        raise UserError(f"Unknown arguments in GET-request: {', '.join(unknown_args)}")

    token = request.args.get('token')
    if not token:
        raise UserError("Account activation token is required.")

    user = User.objects(email_confirmation_token=token).first()
    if not user or not user.is_confirmation_token_valid(token):
        raise UserError("Invalid or expired activation token.")

    user.is_active = True
    user.clear_email_confirmation_token()  # clear token after use
    user.save()

    return jsonify({
        "status": "success",
        "message": "Token is valid. Account is active."
    }), 200
