import re
from backend.src.utils.constants import CITY_NAME_EN_PATTERN, VENUE_PATTERNS, \
    VENUE_TYPE_PATTERNS, EVENT_TYPE_PATTERNS
from backend.src.utils.exceptions import UserError, ConfigurationError


def validate_event_type_data(data):
    """Validate body parameters for event type"""
    for param, value in data.items():
        if not isinstance(value, str):
            raise UserError(f"Parameter '{param}' must be a string.")

        if not re.match(EVENT_TYPE_PATTERNS[param], value):
            match param:
                case 'name_en':
                    raise UserError(
                        "English name must be 3-20 characters long and contain only English letters, spaces and hyphens.")
                case 'name_ru':
                    raise UserError(
                        "Russian name must be 3-20 characters long and contain only Russian letters, spaces and hyphens.")
                case 'name_he':
                    raise UserError(
                        "Hebrew name must be 3-20 characters long and contain only Hebrew letters, spaces and hyphens.")


def validate_venue_type_data(data):
    """Validate body parameters for event type"""
    for param, value in data.items():
        if not isinstance(value, str):
            raise UserError(f"Field '{param}' must be a string")

        if param in VENUE_TYPE_PATTERNS:
            if not re.match(VENUE_TYPE_PATTERNS[param], value):
                match param:
                    case 'name_en':
                        raise UserError(
                            "English name must be 2-30 characters long and contain only English letters, spaces and hyphens")
                    case 'name_ru':
                        raise UserError(
                            "Russian name must be 2-30 characters long and contain only Russian letters, spaces and hyphens")
                    case 'name_he':
                        raise UserError(
                            "Hebrew name must be 2-30 characters long and contain only Hebrew letters, spaces and hyphens")
                    case _:
                        raise ConfigurationError(f"Pattern exists for '{param}' but no error message defined")


def validate_city_data(data):
    """Validate body parameters for city"""
    value_en = data["name_en"]
    if not isinstance(value_en, str):
        raise UserError(f"Parameter 'name_en' must be a string.")

    if not re.match(CITY_NAME_EN_PATTERN, value_en):
        raise UserError(
            "English name must be 3-50 characters long and contain only English letters, spaces and hyphens")


def validate_venue_data(data):
    """Validate body parameters for venue"""
    for param, value in data.items():
        if param == "is_active":
            if not isinstance(data["is_active"], bool):
                raise UserError("Parameter 'is_active' must be boolean")
            continue

        if not isinstance(value, str):
            raise UserError(f"Parameter '{param}' must be a string.")

        # Validate only fields that have patterns
        if param in VENUE_PATTERNS:
            if not re.match(VENUE_PATTERNS[param], value):
                match param:
                    # Names validation messages
                    case 'name_en':
                        raise UserError(
                            "English name must be 3-100 characters long and contain only English letters, spaces and hyphens")
                    case 'name_ru':
                        raise UserError(
                            "Russian name must be 3-100 characters long and contain only Russian letters, spaces and hyphens")
                    case 'name_he':
                        raise UserError(
                            "Hebrew name must be 3-100 characters long and contain only Hebrew letters, spaces and hyphens")

                    # Addresses validation messages
                    case 'address_en':
                        raise UserError(
                            "English address must be 5-200 characters long and contain only English letters, numbers, spaces and basic punctuation")
                    case 'address_ru':
                        raise UserError(
                            "Russian address must be 5-200 characters long and contain only Russian letters, numbers, spaces and basic punctuation")
                    case 'address_he':
                        raise UserError(
                            "Hebrew address must be 5-200 characters long and contain only Hebrew letters, numbers, spaces and basic punctuation")

                    # Descriptions validation messages
                    case 'description_en':
                        raise UserError(
                            "English description must be 20-1000 characters long and contain only English letters, numbers, spaces and punctuation")
                    case 'description_ru':
                        raise UserError(
                            "Russian description must be 20-1000 characters long and contain only Russian letters, numbers, spaces and punctuation")
                    case 'description_he':
                        raise UserError(
                            "Hebrew description must be 20-1000 characters long and contain only Hebrew letters, numbers, spaces and punctuation")

                    # Contact info validation messages
                    case 'phone':
                        raise UserError("Phone number must be 9-15 digits and may start with +")
                    case 'email':
                        raise UserError("Invalid email format")
                    case 'website':
                        raise UserError("Invalid website URL format. Must start with http:// or https://")
                    case 'city_en':
                        raise UserError("City name must contain only English letters, spaces and hyphens")
                    case 'venue_type_en':
                        raise UserError("Venue type must contain only English letters, spaces and hyphens")
                    case _:
                        raise ConfigurationError(f"Pattern exists for '{param}' but no error message defined")
