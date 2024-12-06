from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity
import logging

logger = logging.getLogger('backend')


def get_user_identifier():
    """
    Get unique identifier for rate limiting based on user role+id or IP address.

    Returns:
        str: Format "role:user_id" for authenticated users or "ip:address" for others
    """
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
    """
    Rate limit decorator for public routes.
    Applies 30 requests per minute limit based on IP address.
    """
    return public_routes_limiter.limit(
        "30 per minute",
        error_message="Too many requests from your IP. Please try again later."
    )


def auth_limit():
    """
    Rate limit decorator for authentication routes.
    Applies 3 per minute and 9 per hour limits to prevent brute force attempts.
    """
    return public_routes_limiter.limit(
        "3 per minute, 9 per hour",
        error_message="Too many login attempts. Please try again later."
    )


def protected_routes_limit():
    """
    Rate limit decorator for protected routes.
    Applies different limits based on user role:
    - admin: 60/min
    - manager: 40/min
    - user: 20/min
    - others: 10/min
    """
    def get_limit():
        """
        Determine rate limit based on user role identifier.
        Used in protected_routes_limit decorator.

        Returns:
            str: Rate limit rule (requests per minute)
        """
        identifier = get_user_identifier()
        role = identifier.split(':')[0]

        match role:
            case "admin":
                return "60 per minute"
            case "manager":
                return "40 per minute"
            case "user":
                return "20 per minute"
            case _:
                logger.warning(f"Unauthorized access attempt for protected route from {identifier}")
                return "10 per minute"

    return protected_routes_limiter.limit(
        get_limit,
        error_message="Rate limit exceeded. Try again later."
    )
