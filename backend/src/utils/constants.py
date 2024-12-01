import os
ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg'}

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')

SUPPORTED_LANGUAGES = ["en", "ru", "he"]
DEFAULT_LANGUAGE = "en"

# Venue
ALLOWED_VENUE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "address_en", "address_ru", "address_he",
    "description_en", "description_ru", "description_he",
    "venue_type_en", "city_en", "website", "phone", "email"
}

STRICTLY_REQUIRED_VENUE_BODY_PARAMS = [
    "address_en", "city_en", "venue_type_en"
]

OPTIONAL_VENUE_BODY_PARAMS = [
    "website", "phone", "email"
]

VENUE_PATTERNS = {
    # Names: only letters, spaces and hyphens (3-100 chars)
    'name_en': r'^[a-zA-Z\s-]{3,100}$',
    'name_ru': r'^[а-яА-ЯёЁ\s-]{3,100}$',
    'name_he': r'^[\u0590-\u05FF\s-]{3,100}$',

    # Addresses: letters, digits, basic punctuation (5-200 chars)
    'address_en': r'^[a-zA-Z\s\d,./\-]{5,200}$',
    'address_ru': r'^[а-яА-ЯёЁ\s\d,./\-]{5,200}$',
    'address_he': r'^[\u0590-\u05FF\s\d,./\-]{5,200}$',

    # Descriptions: extended punctuation set (20-1000 chars)
    'description_en': r'^[a-zA-Z\s\d,./\-:;\'\"!?()\[\]]{20,1000}$',
    'description_ru': r'^[а-яА-ЯёЁ\s\d,./\-:;\'\"!?()\[\]]{20,1000}$',
    'description_he': r'^[\u0590-\u05FF\s\d,./\-:;\'\"!?()\[\]]{20,1000}$',

    # References to other entities (English names only)
    'city_en': r'^[a-zA-Z\s\-]{2,30}$',
    'venue_type_en': r'^[a-zA-Z\s\-]{2,30}$',

    # Contact info validation
    'phone': r'^\+?1?\d{9,15}$',
    'email': r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',
    'website': r'^https?:\/\/(www\.)?[\-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([\-a-zA-Z0-9@:%_\+.~#?&//=]*)$'
}

# Event type
ALLOWED_EVENT_TYPE_BODY_PARAMS = {'name_en', 'name_ru', 'name_he'}

EVENT_TYPE_PATTERNS = {
    'name_en': r'^[a-zA-Z\s-]{3,20}$',
    'name_ru': r'^[а-яА-ЯёЁ\s-]{3,20}$',
    'name_he': r'^[\u0590-\u05FF\s-]{3,20}$'
}

# Venue type
ALLOWED_VENUE_TYPE_BODY_PARAMS = {'name_en', 'name_ru', 'name_he'}

VENUE_TYPE_PATTERNS = {
    'name_en': r'^[a-zA-Z\s\-]{2,30}$',
    'name_ru': r'^[а-яА-ЯёЁ\s\-]{2,30}$',
    'name_he': r'^[\u0590-\u05FF\s\-]{2,30}$'
}

# City

CITY_NAME_EN_PATTERN = r'^[a-zA-Z\s-]{3,50}$'



