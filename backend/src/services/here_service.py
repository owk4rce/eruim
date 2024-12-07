import requests
from requests import RequestException
from backend.src.utils.exceptions import UserError, ExternalServiceError


def validate_and_get_location(full_address_he):
    """

    """
    # get env var from conf
    from flask import current_app
    here_api_key = current_app.config["HERE_API_KEY"]

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

        return {
            'type': "Point",
            "coordinates": [
                item["position"]["lng"],
                item["position"]["lat"]
            ]
        }
    except RequestException as e:
        raise ExternalServiceError(f"HERE API Error: {str(e)}")
