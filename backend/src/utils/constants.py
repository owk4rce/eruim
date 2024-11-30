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
    "city_en", "website", "phone", "email"
}

STRICTLY_REQUIRED_VENUE_BODY_PARAMS = [
    'address_en', 'city_en'
]

OPTIONAL_VENUE_BODY_PARAMS = [
    "website", "phone", "email"
]

# Event type
ALLOWED_EVENT_TYPE_BODY_PARAMS = {'name_en', 'name_ru', 'name_he'}

EVENT_TYPE_NAME_PATTERNS = {
    'name_en': r'^[a-zA-Z\s-]{3,20}$',
    'name_ru': r'^[а-яА-ЯёЁ\s-]{3,20}$',
    'name_he': r'^[\u0590-\u05FF\s-]{3,20}$'
}



