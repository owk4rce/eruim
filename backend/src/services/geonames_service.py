from requests import get, RequestException
from backend.src.utils.exceptions import UserError, ExternalServiceError

import logging

logger = logging.getLogger('backend')


def validate_and_get_names(city_name_en):
    """
    Validates city existence in Israel using GeoNames API and retrieves translations.

    Makes a request to GeoNames API to:
    1. Validate that the city exists in Israel
    2. Get its official English name to prevent typos
    3. Retrieve Russian and Hebrew translations

    Args:
        city_name_en (str): English name of the city to validate

    Returns:
        dict: Dictionary containing city names in different languages:
            {
                'en': 'Jerusalem',
                'ru': 'Иерусалим',
                'he': 'ירושלים'
            }

    Raises:
        UserError: If city is not found in Israel or has potential typo
        ExternalServiceError: If GeoNames API request fails or translations missing

    Notes:
        - Uses GeoNames username from application config
        - Filters results to Israel only (country=IL)
        - Requires both Russian and Hebrew translations to be available
    """
    # get env var from config
    from flask import current_app
    geonames_username = current_app.config["GEONAMES_USERNAME"]

    # Search for the city
    search_url = f"http://api.geonames.org/searchJSON"
    params = {
        "q": city_name_en,
        "country": 'IL',  # Filter for Israel
        "maxRows": 1,
        "username": geonames_username,
        "style": "full"
    }

    logger.debug(f"Making GeoNames API request for city: {city_name_en}")

    try:
        response = get(search_url, params=params)
        response.raise_for_status()
    except RequestException as e:
        raise ExternalServiceError(f"GeoNames API error: {str(e)}")

    data = response.json()

    if not data.get("geonames"):
        raise UserError(f"City '{city_name_en}' not found in Israel", 404)

    city_data = data["geonames"][0]

    found_name_en = city_data["name"]

    if found_name_en.lower() != city_name_en.lower():
        raise UserError(f"Maybe you have a typo in the city's name. Found '{found_name_en}'.", 404)

    names = {
        "en": found_name_en,
        "ru": None,
        "he": None
    }

    # Extract Russian and Hebrew names from alternateNames in the response
    for alt_name in city_data.get("alternateNames", []):
        if alt_name.get("lang") == 'ru':
            names["ru"] = alt_name.get("name")
        elif alt_name.get("lang") == "he":
            names["he"] = alt_name.get("name")

    # Validate we have all required names
    if not all([names["ru"], names["he"]]):
        raise ExternalServiceError(
            f"Could not find all required translations for {city_name_en}. "
            f"Found: RU: {names['ru']}, HE: {names['he']}", 404
        )

    logger.info(f"Successfully validated and retrieved translations for city: {city_name_en}")
    logger.debug(f"Retrieved names: {names}")

    return names
