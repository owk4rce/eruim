SUPPORTED_LANGUAGES = ["en", "ru", "he"]
DEFAULT_LANGUAGE = "en"

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
    "website", "phone", "email", "image_path"
]

REQUIRED_EVENT_TYPE_BODY_PARAMS = ['name_en', 'name_ru', 'name_he']

ALLOWED_EVENT_TYPE_BODY_PARAMS = {'name_en', 'name_ru', 'name_he'}