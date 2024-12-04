from backend.src.utils.constants import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE


def validate_language(lang=None):
    """
    Validate language parameter

    Args:
        lang (str): Language type from request

    Returns:
        str: Valid language type or None if invalid
    """
    if not lang:
        return DEFAULT_LANGUAGE

    if lang in SUPPORTED_LANGUAGES:
        return lang

    return None
