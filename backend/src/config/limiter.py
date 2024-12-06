from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity
from flask import current_app


def get_user_identifier():
    """Get user id from JWT if available, otherwise use IP"""
    from backend.src.models.user import User  # avoid cyclic import

    jwt_identity = get_jwt_identity()
    if jwt_identity:
        user = User.objects(id=jwt_identity).first()
        if user:
            return f"{user.role}:{jwt_identity}"  # if jwt, limits by role
    return f"ip:{get_remote_address()}"


# Limiter for public routes
public_routes_limiter = Limiter(
    key_func=get_remote_address,  # just ip
    default_limits=["30 per minute"],
    storage_uri="memory://"
)

# Limiter for protected routes
protected_routes_limiter = Limiter(
    key_func=get_user_identifier,  # ip or logged_user
    storage_uri="memory://"
)


def public_routes_limit():
    """For public routes"""
    if current_app.config.get('TESTING', False):
        return lambda f: f

    return public_routes_limiter.limit(
        "30 per minute",
        error_message="Too many requests from your IP. Please try again later."
    )


def auth_limit():
    """For authentication routes"""
    if current_app.config.get('TESTING', False):
        return lambda f: f

    return public_routes_limiter.limit(
        "5 per minute, 20 per hour",
        error_message="Too many login attempts. Please try again later."
    )


def protected_routes_limit():
    """For protected routes with role-based limits"""
    if current_app.config.get('TESTING', False):
        return lambda f: f

    identifier = get_user_identifier()
    role = identifier.split(':')[0]

    match role:
        case "admin":
            rate_limit = "60 per minute"
        case "manager":
            rate_limit = "40 per minute"
        case "user":
            rate_limit = "20 per minute"
        case _:
            rate_limit = "10 per minute"

    return protected_routes_limiter.limit(
        rate_limit,
        error_message="Rate limit exceeded. Try again later."
    )
