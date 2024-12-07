import secrets


def generate_reset_token(length=32):
    """
    Generate secure random token for password reset

    Args:
        length: Length of token, defaults to 32 characters

    Returns:
        str: Random URL-safe token
    """
    return secrets.token_urlsafe(length)