import requests
from requests import RequestException
from backend.src.utils.exceptions import UserError, ExternalServiceError

import logging

logger = logging.getLogger('backend')


def validate_and_get_location(full_address_he):
    """
    Geocode Hebrew address using HERE API and retrieve coordinates.

    Makes a request to HERE Geocoding API to:
    1. Validate that the address exists in Israel
    2. Get its geographical coordinates (longitude, latitude)

    Args:
        full_address_he (str): Complete address in Hebrew, including city name
            Format: "street_address, city_name"
            Example: "רחוב הרצל 1, תל אביב"

    Returns:
        dict: GeoJSON-style Point object containing coordinates:
            {
                'type': "Point",
                'coordinates': [longitude, latitude]
            }

    Raises:
        UserError: If address is not found
        ExternalServiceError: If HERE API request fails

    Notes:
        - Uses HERE API key from application config
        - Filters results to Israel only (countryCode:ISR)
        - Uses Hebrew language for better accuracy with Hebrew addresses
        - Returns coordinates in [longitude, latitude] format as required by MongoDB
    """
    # get env var from conf
    from flask import current_app
    here_api_key = current_app.config["HERE_API_KEY"]

    logger.debug(f"Making HERE API request for address: {full_address_he}")

    # Search for the address
    search_url = "https://geocode.search.hereapi.com/v1/geocode"

    try:
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

        item = data["items"][0]

        logger.info(f"Successfully geocoded address: {full_address_he}")

        return {
            'type': "Point",
            "coordinates": [
                item["position"]["lng"],
                item["position"]["lat"]
            ]
        }
    except RequestException as e:
        raise ExternalServiceError(f"HERE API Error: {str(e)}")
