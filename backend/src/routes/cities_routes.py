from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import public_routes_limit, protected_routes_limit
from backend.src.controllers.cities_controller import get_all_cities, create_new_city, delete_existing_city, \
    get_existing_city
from backend.src.utils.custom_decorators import no_body_in_request, manager_required, require_json, no_args_in_request, \
    admin_required

# Create Blueprint for cities
cities_bp = Blueprint("cities", __name__, url_prefix="/cities")


@cities_bp.route("/", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_cities():
    """
    Get list of all cities
    ---
    tags:
      - Cities
    parameters:
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
    responses:
      200:
        description: List of cities
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                    description: City name in requested language
                    example: Jerusalem
                  slug:
                    type: string
                    example: jerusalem
            count:
              type: integer
              example: 1
      400:
        description: Invalid language parameter
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: "Unsupported language: fr"
    """
    return get_all_cities()


@cities_bp.route("/<slug>", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_city(slug):
    """
    Get single city by slug
    ---
    tags:
      - Cities
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: City slug
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
    responses:
      200:
        description: City details
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                name:
                  type: string
                  description: City name in requested language
                  example: Jerusalem
                slug:
                  type: string
                  example: jerusalem
      404:
        description: City not found
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: "City with slug jerusalem not found"
    """
    return get_existing_city(slug)


@cities_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def create_city():
    """
    Create new city
    ---
    tags:
      - Cities
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name_en
          properties:
            name_en:
              type: string
              description: English name of the city
              example: Jerusalem
    responses:
      201:
        description: City created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: City created successfully
            data:
              type: object
              properties:
                name_ru:
                  type: string
                  example: Иерусалим
                name_en:
                  type: string
                  example: Jerusalem
                name_he:
                  type: string
                  example: ירושלים
                slug:
                  type: string
                  example: jerusalem
      409:
        description: City already exists
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: "City with name Jerusalem already exists"
      404:
        description: City not found in Israel
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: "City 'Jerusalem' not found in Israel"
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
    """
    return create_new_city()


@cities_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@admin_required()
@no_body_in_request()
@no_args_in_request()
def delete_city(slug):
    """
    Delete city
    ---
    tags:
      - Cities
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: City slug
    responses:
      204:
        description: City successfully deleted
      404:
        description: City not found
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: "City with slug 'jerusalem' not found"
      409:
        description: Cannot delete city with associated venues
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: "Cannot delete this city. Please delete all associated venues first."
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
    """
    return delete_existing_city(slug)
