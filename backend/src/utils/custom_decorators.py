from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity
from functools import wraps

from backend.src.utils.exceptions import UserError


# Auth decorators
def check_active_user():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from backend.src.models.user import User    # to avoid cyclic imports

            current_user_id = get_jwt_identity()
            user = User.objects(id=current_user_id).first()

            if not user:
                raise UserError("User not found", 404)

            if not user.is_active:
                response = jsonify({
                    "status": "error",
                    "message": "Account is inactive"
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
    def decorator(f):
        @wraps(f)
        @check_active_user()  # even admin could be inactive
        def decorated_function(*args, **kwargs):
            from backend.src.models.user import User  # to avoid cyclic imports

            current_user_id = get_jwt_identity()
            user = User.objects(id=current_user_id).first()

            if not user.is_admin():  # not admin?
                raise UserError("Admin access required", 403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def manager_required():
    def decorator(f):
        @wraps(f)
        @check_active_user()  # even manager could be inactive
        def decorated_function(*args, **kwargs):
            from backend.src.models.user import User  # to avoid cyclic imports

            current_user_id = get_jwt_identity()
            user = User.objects(id=current_user_id).first()

            if not user.can_manage_content():  # no manager privileges?
                raise UserError("Manager access required", 403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Request decorators-

def no_body_in_request():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.data or request.form or request.files:
                raise UserError("Using body in this request is restricted.")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def no_args_in_request():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.args:
                raise UserError("Arguments in this request are restricted.")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_json():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise UserError("Content-Type must be application/json.", 415)
            data = request.get_json()
            if not data:
                raise UserError("Body parameters are missing.")
            return f(*args, **kwargs)

        return decorated_function

    return decorator
