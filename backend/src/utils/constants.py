import os
import pytz

TIMEZONE = pytz.timezone('Asia/Jerusalem')

ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg'}

IMAGE_PATHS = {
    "venues": "/uploads/img/venues/{slug}/{filename}",
    "events": "/uploads/img/events/{slug}/{filename}"
}

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')

# Add logs path
LOGS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

SUPPORTED_LANGUAGES = ["en", "ru", "he"]
DEFAULT_LANGUAGE = "en"

# Venue
ALLOWED_VENUE_GET_ALL_ARGS = {
    "lang", "is_active", "city"
}

ALLOWED_VENUE_CREATE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "address_en",
    "description_en", "description_ru", "description_he",
    "venue_type_en", "city_en", "website", "phone", "email"
}

ALLOWED_VENUE_UPDATE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "address_en", "address_he", "address_ru",
    "description_en", "description_ru", "description_he",
    "venue_type_en", "city_en", "website", "phone", "email",
    "is_active"
}

STRICTLY_REQUIRED_VENUE_CREATE_BODY_PARAMS = {
    "address_en", "city_en", "venue_type_en"
}

VENUE_PATTERNS = {
    # Names: letters, digits, spaces, hyphens, dashes, quotes (3-100 chars)
    'name_en': r'^[a-zA-Z\d\s\-–—\'\"«»]{3,100}$',
    'name_ru': r'^[а-яА-ЯёЁ\d\s\-–—\'\"«»„"]{3,100}$',
    'name_he': r'^[\u0590-\u05FF\d\s\-–—\'\"«»״׳]{3,100}$',

    # Addresses: letters, digits, basic punctuation (5-200 chars)
    'address_en': r'^[a-zA-Z\s\d,./\-]{5,200}$',
    'address_ru': r'^[а-яА-ЯёЁ\s\d,./\-]{5,200}$',
    'address_he': r'^[\u0590-\u05FF\s\d,./\-]{5,200}$',

    # Descriptions: extended punctuation set (20-1000 chars)
    'description_en': r'^[a-zA-Z\s\d,./\-–—:;\'\"«»!?()\[\]]{20,1000}$',
    'description_ru': r'^[а-яА-ЯёЁ\s\d,./\-–—:;\'\"«»„""!?()\[\]]{20,1000}$',
    'description_he': r'^[\u0590-\u05FF\s\d,./\-–—:;\'\"«»!?()\[\]]{20,1000}$',

    # References to other entities (English names only)
    'city_en': r'^[a-zA-Z\s\-]{2,30}$',
    'venue_type_en': r'^[a-zA-Z\s\-]{2,30}$',

    # Contact info validation
    'phone': r'^\+?1?\d{9,15}$',
    'email': r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',
    'website': r'^https?:\/\/(www\.)?[\-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([\-a-zA-Z0-9@:%_\+.~#?&//=]*)$'
}

# Event
PRICE_TYPES = ['free', 'tba', 'fixed', 'starting_from']

PRICE_TYPE_TRANSLATIONS = {
    'free': {
        'en': 'Free',
        'ru': 'Бесплатно',
        'he': 'חינם'
    },
    'tba': {
        'en': 'TBA',
        'ru': 'Уточняется',
        'he': 'יפורסם בהמשך'
    },
    'fixed': {
        'en': 'Fixed price',
        'ru': 'Фиксированная цена',
        'he': 'מחיר קבוע'
    },
    'starting_from': {
        'en': 'From',
        'ru': 'От',
        'he': 'החל מ'
    }
}

ALLOWED_EVENT_GET_ALL_ARGS = {
    "lang", "is_active", "city", "venue", "sort"
}

ALLOWED_EVENT_CREATE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "description_en", "description_ru", "description_he",
    "venue_slug", "event_type_slug",
    "start_date", "end_date",
    "price_type", "price_amount"
}

ALLOWED_EVENT_UPDATE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "description_en", "description_ru", "description_he",
    "venue_slug", "event_type_slug",
    "start_date", "end_date",
    "price_type", "price_amount",
    "is_active"
}

STRICTLY_REQUIRED_EVENT_CREATE_BODY_PARAMS = {
    "venue_slug", "event_type_slug", "start_date", "end_date", "price_type"
}

EVENT_PATTERNS = {
    # Names (3-200 chars)
    'name_en': r'^[a-zA-Z\d\s\-–—\'\"«»:]{3,200}$',
    'name_ru': r'^[а-яА-ЯёЁ\d\s\-–—\'\"«»„":]{3,200}$',
    'name_he': r'^[\u0590-\u05FF\d\s\-–—\'\"«»״׳:]{3,200}$',

    # Descriptions (20-2000 chars)
    'description_en': r'^[a-zA-Z\d\s\-–—.,!?()\'\"«»:\[\];]{20,2000}$',
    'description_ru': r'^[а-яА-ЯёЁ\d\s\-–—.,!?()\'\"«»„":\[\];]{20,2000}$',
    'description_he': r'^[\u0590-\u05FF\d\s\-–—.,!?()\'\"«»״׳:\[\];]{20,2000}$'
}


# Event type
ALLOWED_EVENT_TYPE_BODY_PARAMS = {'name_en', 'name_ru', 'name_he'}

EVENT_TYPE_PATTERNS = {
    'name_en': r'^[a-z\s-]{3,20}$',
    'name_ru': r'^[а-яё\s-]{3,20}$',
    'name_he': r'^[\u0590-\u05FF\s-]{3,20}$'
}

# Venue type
ALLOWED_VENUE_TYPE_GET_ALL_ARGS = {
    "lang"
}

ALLOWED_VENUE_TYPE_BODY_PARAMS = {'name_en', 'name_ru', 'name_he'}

VENUE_TYPE_PATTERNS = {
    'name_en': r'^[a-z\s-]{2,30}$',
    'name_ru': r'^[а-яё\s-]{2,30}$',
    'name_he': r'^[\u0590-\u05FF\s\-]{2,30}$'
}

# City

CITY_NAME_EN_PATTERN = r'^[a-zA-Z\s-]{3,50}$'

# User

ALLOWED_USER_BODY_PARAMS = {'email', 'password', 'role', "is_active", "default_lang"}

REQUIRED_USER_BODY_PARAMS = {'email', 'password', 'role'}

USER_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'password': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
    'role': r'^(admin|manager|user)$',
    'default_lang': r'^(en|ru|he)$'
}

# profile

ALLOWED_PROFILE_BODY_PARAMS = {'email', "password", "default_lang"}

# auth

ALLOWED_AUTH_BODY_PARAMS = {'email', "password", "default_lang"}

REQUIRED_AUTH_BODY_PARAMS = {'email', "password"}


