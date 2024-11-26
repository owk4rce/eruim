from flask import Blueprint, jsonify, request
from mongoengine.connection import get_db
from backend.src.models.city import City
from backend.src.utils.exceptions import ConfigurationError, CityGeoNameError, CityValidationError
from mongoengine.errors import ValidationError, NotUniqueError
from werkzeug.exceptions import BadRequest
from slugify import slugify
from backend.src.services.geonames_service import validate_and_get_names


# Create Blueprint for cities
cities_bp = Blueprint('cities', __name__, url_prefix='/cities')


@cities_bp.route("/", methods=["GET"])
def get_cities():
    """
    Get list of all cities

    Query Parameters:
        - lang (str, optional): Language for city names (en, ru, he). Defaults to 'en'

    Returns:
        JSON response with:
        - status: success/error
        - data: list of cities or error message
        - count: total number of cities (only if successful)
    """
    try:
        # Get language preference from query parameter, default to English
        language = request.args.get('lang', 'en')
        if language not in ['en', 'ru', 'he']:
            return jsonify({
                'status': 'error',
                'message': f'Unsupported language: {language}'
            }), 400

        # Get all active cities from database
        cities = City.objects()
        # Format response data using the requested language
        cities_data = [{
            'name': city.get_name(language),
            'slug': city.slug
        } for city in cities]

        return jsonify({
            'status': 'success',
            'data': cities_data,
            'count': len(cities_data)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@cities_bp.route("/", methods=["POST"])
def add_city():
    try:
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 415

        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Body parameters are missing.'
            }), 400

        if len(data) != 1 or 'name_en' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Body of request must contain only name_en field'
            }), 400

        names = validate_and_get_names(data['name_en'])

        city = City(name_en=names["en"],
                    name_ru=names["ru"],
                    name_he=names["he"],
                    slug=slugify(names['en'])
                    )
        city.save()

        return jsonify({
            'status': 'success',
            'message': 'City created successfully'
        }), 201

    except BadRequest:  # Empty or invalid JSON
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format or empty request body'
        }), 400

    except ValidationError as e:  # MongoEngine validation errors (regex, min_length, etc.)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

    except CityValidationError as e:  #
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

    except NotUniqueError:  # Duplicate key error
        return jsonify({
            'status': 'error',
            'message': 'City with this name already exists'
        }), 409

    except ConfigurationError as e:  # Server configuration error
        return jsonify({
            'status': 'error',
            'message': str(e)  # Internal Server Error
        }), 500

    except CityGeoNameError as e:  # GeoNames API service error
        return jsonify({
            'status': 'error',
            'message': str(e)  # Service Unavailable
        }), 503

    except Exception as e:  # Unexpected errors
        print(f"Error type: {type(e)}, Message: {str(e)}")
        print(f"Error in add_city: {str(e)}")  # log for debugging
        return jsonify({
            'status': 'error',
            'message': 'Internal Server Error'
        }), 500
