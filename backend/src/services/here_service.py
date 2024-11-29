import os

import requests
from requests import RequestException

from backend.src.services.translation_service import translate_with_google
from backend.src.utils.constants import SUPPORTED_LANGUAGES
from backend.src.utils.exceptions import ConfigurationError, UserError, ExternalServiceError


def validate_and_get_addr_and_location(full_address_en):
    """
    Validates address using HERE API and returns addresses in different languages and location
    """
    here_api_key = os.getenv('HERE_API_KEY')
    if not here_api_key:
        raise ConfigurationError("HERE_API_KEY not set in .env")

    full_address_he = translate_with_google(full_address_en, "en", "iw")

    # Search for the address
    search_url = "https://geocode.search.hereapi.com/v1/geocode"
    addresses = {}

    try:
        # for lang in SUPPORTED_LANGUAGES:
        params = {
            "q": full_address_he,
            "apiKey": here_api_key,
            "lang": "he",
            "in": "countryCode:ISR"
        }

        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data["items"]:
            raise UserError(f"Address not found: {full_address_he}", 404)

            # if lang == "ru" and len(data["items"]) > 1:  # for russian language it is on the 1 place
            #     item = data["items"][1]
            # else:
            #     item = data["items"][0]

        item = data["items"][0]

        addresses["en"] = full_address_en
        addresses["he"] = item["address"]["label"]
        full_address_ru = translate_with_google(addresses["he"], "iw", "ru")
        addresses["ru"] = full_address_ru

        # Store coordinates
        addresses['location'] = {
            'type': 'Point',
            'coordinates': [
                item['position']['lng'],
                item['position']['lat']
            ]
        }

        return addresses

    except RequestException as e:
        raise ExternalServiceError(f"HERE API Error: {str(e)}")
