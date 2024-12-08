from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity
from functools import wraps

from backend.src.utils.exceptions import UserError

import logging

logger = logging.getLogger('backend')


# Auth decorators
def check_active_user():
    """
    Decorator that checks if the authenticated user is active.

    If user is inactive:
    - Removes JWT token cookie
    - Returns 403 Forbidden response

    Used primarily for profile and content management routes to ensure
    user has not been deactivated during their session.

    Returns:
        function: Decorated route handler

    Raises:
        UserError: If user not found
        Returns 403: If user is inactive
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from backend.src.models.user import User  # to avoid cyclic imports

            current_user_id = get_jwt_identity()
            user = User.objects(id=current_user_id).first()

            if not user:
                logger.warning(f"User not found with ID: {current_user_id}")
                raise UserError("User not found", 404)

            if not user.is_active:
                logger.warning(f"Inactive user attempted access: {user.email}")
                response = jsonify({
                    "status": "error",
                    "message": "Account is inactive."
                })
                # if user became inactive during token/cookie life
                response.delete_cookie(
                    'token',
                    httponly=True,
                    secure=current_app.config["JWT_COOKIE_SECURE"],
                    samesite='Strict'
                )

                return response, 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required():
    """
    Decorator that ensures user has admin role.

    Combines check_active_user decorator with admin role verification.
    Used for administrative routes like user management.

    Returns:
        function: Decorated route handler

    Raises:
        UserError: If user lacks admin role (403)
    """
    def decorator(f):
        @wraps(f)
        @check_active_user()  # even admin could be inactive
        def decorated_function(*args, **kwargs):
            from backend.src.models.user import User  # to avoid cyclic imports

            current_user_id = get_jwt_identity()
            user = User.objects(id=current_user_id).first()

            if not user.is_admin():  # not admin?
                logger.warning(f"Non-admin user attempted admin action: {user.email}")
                raise UserError("Admin access required", 403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def manager_required():
    """
    Decorator that ensures user has manager or admin role.

    Combines check_active_user decorator with role verification.
    Used for content management routes (venues, events, etc.).

    Returns:
        function: Decorated route handler

    Raises:
        UserError: If user lacks required role (403)
    """
    def decorator(f):
        @wraps(f)
        @check_active_user()  # even manager could be inactive
        def decorated_function(*args, **kwargs):
            from backend.src.models.user import User  # to avoid cyclic imports

            current_user_id = get_jwt_identity()
            user = User.objects(id=current_user_id).first()

            if not user.can_manage_content():  # no manager privileges?
                logger.warning(f"Non-manager user attempted content management: {user.email}")
                raise UserError("Manager access required", 403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Request decorators-

def no_body_in_request():
    """
    Decorator that ensures request has no body parameters.

    Used for GET and DELETE requests where body is inappropriate.

    Returns:
        function: Decorated route handler

    Raises:
        UserError: If request contains body data
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.data or request.form or request.files:
                logger.warning(f"Request to {request.path} contained unexpected body")
                raise UserError("Using body in this request is restricted.")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def no_args_in_request():
    """
    Decorator that ensures request has no query parameters.

    Used for routes where query parameters are not expected.

    Returns:
        function: Decorated route handler

    Raises:
        UserError: If request contains query parameters
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.args:
                logger.warning(f"Request to {request.path} contained unexpected query parameters")
                raise UserError("Arguments in this request are restricted.")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_json():
    """
    Decorator that ensures request has JSON content type and body.

    Used for POST/PUT/PATCH routes that expect JSON data.

    Returns:
        function: Decorated route handler

    Raises:
        UserError: If content type is not application/json or body is empty
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                logger.warning(f"Non-JSON request to {request.path}")
                raise UserError("Content-Type must be application/json.", 415)
            data = request.get_json()
            if not data:
                logger.warning(f"Empty JSON body in request to {request.path}")
                raise UserError("Body parameters are missing.")
            return f(*args, **kwargs)

        return decorated_function

    return decorator
