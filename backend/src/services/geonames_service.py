from requests import get, RequestException
from backend.src.utils.exceptions import ConfigurationError, UserError, ExternalServiceError
import os


def validate_and_get_names(city_name_en):
    """
    Validates city using GeoNames API and returns names in different languages
    """
    geonames_username = os.getenv("GEONAMES_USERNAME")
    if not geonames_username:
        raise ConfigurationError("GEONAMES_USERNAME not set in .env")

    # Search for the city
    search_url = f"http://api.geonames.org/searchJSON"
    params = {
        "q": city_name_en,
        "country": 'IL',  # Filter for Israel
        'maxRows': 1,
        "username": geonames_username,
        "style": "full"
    }

    try:
        response = get(search_url, params=params)
        response.raise_for_status()
    except RequestException as e:
        raise ExternalServiceError(f"GeoNames API error: {str(e)}")

    data = response.json()

    if not data.get("geonames"):
        raise UserError(f"City '{city_name_en}' not found in Israel", 404)

    city_data = data['geonames'][0]

    found_name_en = city_data["name"]

    if found_name_en.lower() != city_name_en.lower():
        raise UserError(f"Maybe you have a typo in the city's name. Found '{found_name_en}'.", 404)

    names = {
        'en': found_name_en,
        'ru': None,
        'he': None
    }

    # Extract Russian and Hebrew names from alternateNames in the response
    for alt_name in city_data.get('alternateNames', []):
        if alt_name.get('lang') == 'ru':
            names['ru'] = alt_name.get('name')
        elif alt_name.get('lang') == 'he':
            names['he'] = alt_name.get('name')

    # Validate we have all required names
    if not all([names['ru'], names['he']]):
        raise ExternalServiceError(
            f"Could not find all required translations for {city_name_en}. "
            f"Found: RU: {names['ru']}, HE: {names['he']}", 404
        )

    return names


