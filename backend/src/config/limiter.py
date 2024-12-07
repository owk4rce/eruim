from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity
import logging

logger = logging.getLogger('backend')


def get_user_identifier():
    """
    Get unique identifier for rate limiting based on user authentication status.

    For authenticated users, returns string in format "role:user_id" to enable
    role-based rate limiting. For unauthenticated users, returns "ip:address".

    This allows different rate limits for different user roles while still
    maintaining rate limiting for anonymous users.

    Returns:
        str: Identifier in format "role:user_id" or "ip:address"
    """
    from backend.src.models.user import User  # avoid cyclic import

    jwt_identity = get_jwt_identity()
    if jwt_identity:
        user = User.objects(id=jwt_identity).first()
        if user:
            logger.debug(f"Rate limit identifier created for {user.role} user: {jwt_identity}")
            return f"{user.role}:{jwt_identity}"  # if jwt, limits by role
    ip = get_remote_address()
    logger.debug(f"Rate limit identifier created for IP: {ip}")
    return f"ip:{ip}"


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

    Applies a general rate limit of 30 requests per minute based on IP address.
    This helps prevent abuse of public endpoints while allowing reasonable usage.

    Returns:
        function: Limiter decorator configured for public routes
    """
    return public_routes_limiter.limit(
        "30 per minute",
        error_message="Too many requests from your IP. Please try again later."
    )


def auth_limit():
    """
    Rate limit decorator specifically for authentication routes.

    Applies stricter limits to prevent brute force attacks:
    - 3 requests per minute
    - 9 requests per hour

    Returns:
        function: Limiter decorator configured for authentication routes
    """
    return public_routes_limiter.limit(
        "3 per minute, 9 per hour",
        error_message="Too many login attempts. Please try again later."
    )


def protected_routes_limit():
    """
    Rate limit decorator for protected routes with role-based limits.

    Applies different limits based on user role:
    - Admin: 60 requests per minute
    - Manager: 40 requests per minute
    - User: 20 requests per minute
    - Unauthenticated: 10 requests per minute

    Returns:
        function: Limiter decorator with dynamic limits based on user role
    """
    def get_limit():
        """
        Determine specific rate limit based on user role.

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
