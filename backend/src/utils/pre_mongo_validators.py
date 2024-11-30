import re
from backend.src.utils.constants import EVENT_TYPE_NAME_PATTERNS
from backend.src.utils.exceptions import UserError


def validate_event_type_data(data):
    """Validate body parameters for event type"""
    for param, value in data.items():
        if not isinstance(value, str):
            raise UserError(f"Parameter '{param}' must be a string")

        if not re.match(EVENT_TYPE_NAME_PATTERNS[param], value):
            match param:
                case 'name_en':
                    raise UserError(
                        "English name must be 3-20 characters long and contain only English letters, spaces and hyphens")
                case 'name_ru':
                    raise UserError(
                        "Russian name must be 3-20 characters long and contain only Russian letters, spaces and hyphens")
                case 'name_he':
                    raise UserError(
                        "Hebrew name must be 3-20 characters long and contain only Hebrew letters, spaces and hyphens")
