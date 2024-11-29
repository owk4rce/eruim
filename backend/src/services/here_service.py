import os

import requests
from requests import RequestException
from backend.src.utils.constants import SUPPORTED_LANGUAGES
from backend.src.utils.exceptions import ConfigurationError, UserError, ExternalServiceError


def validate_and_get_addr_and_location(full_address_en):
    """
    Validates address using HERE API and returns addresses in different languages and location
    """
    here_api_key = os.getenv('HERE_API_KEY')
    if not here_api_key:
        raise ConfigurationError("HERE_API_KEY not set in .env")

    # Search for the address
    search_url = "https://geocode.search.hereapi.com/v1/geocode"
    addresses = {}

    try:
        for lang in SUPPORTED_LANGUAGES:
            params = {
                "q": full_address_en,
                "apiKey": here_api_key,
                "lang": lang,
                "in": "countryCode:ISR"
            }

            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data["items"]:
                raise UserError(f"Address not found: {full_address_en}", 404)

            if lang == "ru" and len(data["items"]) > 1:  # for russian language it is on the 1 place
                item = data["items"][1]
            else:
                item = data["items"][0]

            addresses[lang] = item["address"]["label"]

            # Store coordinates from first response only
            if lang == 'en':
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
