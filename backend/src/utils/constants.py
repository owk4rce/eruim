import os
import pytz

# Timezone configuration
TIMEZONE = pytz.timezone('Asia/Jerusalem')

# Image file handling
ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# File paths configuration
IMAGE_PATHS = {
    "venues": "/uploads/img/venues/{slug}/{filename}",
    "events": "/uploads/img/events/{slug}/{filename}"
}

# Get absolute paths for uploads and logs from project root
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')

LOGS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

# Languages configuration
SUPPORTED_LANGUAGES = ["en", "ru", "he"]
DEFAULT_LANGUAGE = "en"

# ===================== Venue Constants =====================
# Query parameters allowed for GET /venues/
ALLOWED_VENUE_GET_ALL_ARGS = {
    "lang", "is_active", "city"
}

# Body parameters allowed for POST /venues/
ALLOWED_VENUE_CREATE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "address_en",
    "description_en", "description_ru", "description_he",
    "venue_type_en", "city_en", "website", "phone", "email"
}

# Body parameters allowed for PUT, PATCH /venues/{slug}
ALLOWED_VENUE_UPDATE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "address_en", "address_he", "address_ru",
    "description_en", "description_ru", "description_he",
    "venue_type_en", "city_en", "website", "phone", "email",
    "is_active"
}

# Required parameters for venue creation
STRICTLY_REQUIRED_VENUE_CREATE_BODY_PARAMS = {
    "address_en", "city_en", "venue_type_en"
}

# Regex patterns for venue fields validation
VENUE_PATTERNS = {
    # Names: letters, digits, spaces, hyphens, dashes, quotes (3-100 chars)
    'name_en': r'^[a-zA-Z\d\s\-–—\'\"«»]{3,100}$',
    'name_ru': r'^[а-яА-ЯёЁ\d\s\-–—\'\"«»„"]{3,100}$',
    'name_he': r'^[\u0590-\u05FF\d\s\-–—\'\"«»״׳]{3,100}$',

    # Addresses: letters, digits, basic punctuation (5-200 chars)
    'address_en': r'^[a-zA-Z\s\d,./\-\']{5,200}$',
    'address_ru': r'^[а-яА-ЯёЁ\s\d,./\-\']{5,200}$',
    'address_he': r'^[\u0590-\u05FF\s\d,./\-\׳\']{5,200}$',

    # Descriptions: extended punctuation set (20-1000 chars)
    'description_en': r'^[a-zA-Z\s\d,./\-–—:;\'\"«»!?(’)\[\]]{20,1000}$',
    'description_ru': r'^[а-яА-ЯёЁ\s\d,./\-–—:;\'\"«»„""!?(’)\[\]]{20,1000}$',
    'description_he': r'^[\u0590-\u05FF\s\d,./\-–—:;\'\"«»!?(’)\[\]]{20,1000}$',

    # References to other entities (English names only)
    'city_en': r'^[a-zA-Z\s\-]{2,30}$',
    'venue_type_en': r'^[a-zA-Z\s\-]{2,30}$',

    # Contact info validation
    'phone': r'^\+?1?\d{9,15}$',
    'email': r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',
    'website': r'^https?:\/\/(www\.)?[\-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([\-a-zA-Z0-9@:%_\+.~#?&//=]*)$'
}

# ===================== Event Constants =====================
# Price type configurations
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

# Query parameters allowed for GET /events/
ALLOWED_EVENT_GET_ALL_ARGS = {
    "lang", "is_active", "city", "venue", "type", "sort"
}

# Body parameters allowed for POST /events/
ALLOWED_EVENT_CREATE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "description_en", "description_ru", "description_he",
    "venue_slug", "event_type_slug",
    "start_date", "end_date",
    "price_type", "price_amount"
}

# Body parameters allowed for PUT, PATCH /events/{slug}
ALLOWED_EVENT_UPDATE_BODY_PARAMS = {
    "name_en", "name_ru", "name_he",
    "description_en", "description_ru", "description_he",
    "venue_slug", "event_type_slug",
    "start_date", "end_date",
    "price_type", "price_amount",
    "is_active"
}

# Required parameters for event creation
STRICTLY_REQUIRED_EVENT_CREATE_BODY_PARAMS = {
    "venue_slug", "event_type_slug", "start_date", "end_date", "price_type"
}

# Regex patterns for event fields validation
EVENT_PATTERNS = {
    # Names (3-200 chars)
    'name_en': r'^[a-zA-Z\d\s\-–—\'\"«»:]{3,200}$',
    'name_ru': r'^[а-яА-ЯёЁ\d\s\-–—\'\"«»„":]{3,200}$',
    'name_he': r'^[\u0590-\u05FF\d\s\-–—\'\"«»״׳:]{3,200}$',

    # Descriptions (20-2000 chars)
    'description_en': r'^[a-zA-Z\d\s\-–—.,!?(’)\'\"«»:\[\];]{20,2000}$',
    'description_ru': r'^[а-яА-ЯёЁ\d\s\-–—.,!?()\'\"«»„":\[\];]{20,2000}$',
    'description_he': r'^[\u0590-\u05FF\d\s\-–—.,!?()\'\"«»״׳:\[\];]{20,2000}$'
}

# ===================== Event Type Constants =====================
# Body parameters allowed for POST, PUT, PATCH /event_types/
ALLOWED_EVENT_TYPE_BODY_PARAMS = {'name_en', 'name_ru', 'name_he'}

# Regex patterns for event type validation
EVENT_TYPE_PATTERNS = {
    'name_en': r'^[a-z\s-]{3,20}$',
    'name_ru': r'^[а-яё\s-]{3,20}$',
    'name_he': r'^[\u0590-\u05FF\s-]{3,20}$'
}

# ===================== Venue Type Constants =====================
# Query parameters allowed for GET /venue_types/
ALLOWED_VENUE_TYPE_GET_ALL_ARGS = {
    "lang"
}

# Body parameters allowed for POST, PUT, PATCH /venue_types/
ALLOWED_VENUE_TYPE_BODY_PARAMS = {'name_en', 'name_ru', 'name_he'}

# Regex patterns for venue type validation
VENUE_TYPE_PATTERNS = {
    'name_en': r'^[a-z\s-]{2,30}$',
    'name_ru': r'^[а-яё\s-]{2,30}$',
    'name_he': r'^[\u0590-\u05FF\s\-]{2,30}$'
}

# ===================== City Constants =====================
# Regex pattern for city name validation
CITY_NAME_EN_PATTERN = r'^[a-zA-Z\s-]{3,50}$'

# ===================== User Constants =====================
# Body parameters allowed for user operations
ALLOWED_USER_BODY_PARAMS = {'email', 'password', 'role', "is_active", "default_lang"}

REQUIRED_USER_BODY_PARAMS = {'email', 'password', 'role'}

# Regex patterns for user validation
USER_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'password': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
    'role': r'^(admin|manager|user)$',
    'default_lang': r'^(en|ru|he)$'
}

# ===================== Profile Constants =====================
ALLOWED_PROFILE_BODY_PARAMS = {'email', "password", "default_lang"}

# ===================== Auth Constants =====================
ALLOWED_AUTH_BODY_PARAMS = {'email', "password", "default_lang"}

REQUIRED_AUTH_BODY_PARAMS = {'email', "password"}


