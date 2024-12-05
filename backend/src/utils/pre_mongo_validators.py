import re
from datetime import datetime
from backend.src.utils.constants import CITY_NAME_EN_PATTERN, VENUE_PATTERNS, \
    VENUE_TYPE_PATTERNS, EVENT_TYPE_PATTERNS, USER_PATTERNS, EVENT_PATTERNS, PRICE_TYPES
from backend.src.utils.exceptions import UserError, ConfigurationError


def validate_user_data(data):
    """Validate body parameters for user"""
    for param, value in data.items():
        if param == "is_active":
            if not isinstance(data["is_active"], bool):
                raise UserError("Parameter 'is_active' must be boolean")
            continue

        if not isinstance(value, str):
            raise UserError(f"Parameter '{param}' must be a string.")

        # Validate only fields that have patterns
        if param in USER_PATTERNS:
            if not re.match(USER_PATTERNS[param], value):
                match param:
                    case 'email':
                        raise UserError("Invalid email format")
                    case 'password':
                        raise UserError(
                            'Password requirements: '
                            'At least 8 characters long. '
                            'Only English letters (a-z, A-Z). '
                            'At least one uppercase letter. '
                            'At least one lowercase letter. '
                            'At least one number. '
                            'At least one special character (@$!%*?&).'
                        )
                    case 'role':
                        raise UserError("Invalid role. Must be one of: admin, manager, user")
                    case 'default_lang':
                        raise UserError("Invalid language. Must be one of: en, ru, he")
                    case _:
                        raise ConfigurationError(f"Pattern exists for '{param}' but no error message defined")


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
            if not isinstance(value, bool):
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
                            "English name must be 3-100 characters long and contain only English letters, "
                            "numbers, spaces, hyphens (-, –, —), and quotes (', \", «, »)")
                    case 'name_ru':
                        raise UserError(
                            "Russian name must be 3-100 characters long and contain only Russian letters, "
                            "numbers, spaces, hyphens (-, –, —), and quotes (', \", «, », „, \")")
                    case 'name_he':
                        raise UserError(
                            "Hebrew name must be 3-100 characters long and contain only Hebrew letters, "
                            "numbers, spaces, hyphens (-, –, —), and quotes (', \", «, », ״, ׳)")

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


def validate_event_data(data):
    """

    """
    # Validate patterns for provided text fields
    for param, value in data.items():
        if param == "price_amount":
            if not isinstance(value, int):
                raise UserError("Parameter 'price_amount' must be integer.")
            continue
        if param in ["start_date", "end_date"]:
            continue

        if not isinstance(value, str):
            raise UserError(f"Parameter '{param}' must be a string.")

        if param in EVENT_PATTERNS:
            if not re.match(EVENT_PATTERNS[param], value):
                match param:
                    case 'name_en':
                        raise UserError(
                            "English name must be 3-200 characters long and contain only English letters, "
                            "numbers, spaces, hyphens (-, –, —), and quotes (', \", «, »)"
                        )
                    case 'name_ru':
                        raise UserError(
                            "Russian name must be 3-200 characters long and contain only Russian letters, "
                            "numbers, spaces, hyphens (-, –, —), and quotes (', \", «, », „, \")"
                        )
                    case 'name_he':
                        raise UserError(
                            "Hebrew name must be 3-200 characters long and contain only Hebrew letters, "
                            "numbers, spaces, hyphens (-, –, —), and quotes (', \", «, », ״, ׳)"
                        )
                    case 'description_en':
                        raise UserError(
                            "English description must be 20-2000 characters long and contain only English letters, "
                            "numbers, spaces and punctuation"
                        )
                    case 'description_ru':
                        raise UserError(
                            "Russian description must be 20-2000 characters long and contain only Russian letters, "
                            "numbers, spaces and punctuation"
                        )
                    case 'description_he':
                        raise UserError(
                            "Hebrew description must be 20-2000 characters long and contain only Hebrew letters, "
                            "numbers, spaces and punctuation"
                        )

    # Validate dates format and logic
    if data["end_date"] < data["start_date"]:
        raise UserError("End date must be after start date.")

    # Check if start date is not in past
    if not is_valid_end_time(data["end_date"]):
        raise UserError('Event cannot end in the past or before current time.')

    # Validate price logic
    if "price_type" in data:
        if data["price_type"] not in PRICE_TYPES:
            raise UserError(f"Invalid price type. Must be one of: {', '.join(PRICE_TYPES)}")

        if data["price_type"] in ["fixed", "starting_from"]:
            if "price_amount" not in data:
                raise UserError("Price amount is required for 'fixed' and 'starting_from' price types.")

            if data['price_amount'] < 0:
                raise UserError("Price amount cannot be negative.")

        elif "price_amount" in data:
            raise UserError("Price amount should not be set for free or TBA events.")


def is_valid_end_time(start_date):
    """
    Check if event start time is valid (not in past and at least current time)
    Returns True if start_date is valid
    """
    now = datetime.utcnow()

    # If date is today, check if time is future
    if start_date.date() == now.date():
        return start_date.time() > now.time()

    # If different date, check if future date
    return start_date.date() > now.date()
