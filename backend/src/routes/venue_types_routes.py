from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import public_routes_limit, protected_routes_limit
from backend.src.controllers.venue_types_controller import get_all_venue_types, create_new_venue_type, \
    full_update_existing_venue_type, part_update_existing_venue_type, delete_existing_venue_type, \
    get_existing_venue_type
from backend.src.utils.custom_decorators import no_body_in_request, manager_required, require_json, no_args_in_request

# Create Blueprint for venue types
venue_types_bp = Blueprint("venue_types", __name__, url_prefix="/venue_types")


@venue_types_bp.route("/", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_venue_types():
    """
    Get list of venue types
    ---
    tags:
      - Venue Types
    parameters:
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
    responses:
      200:
        description: List of venue types
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
                    example: museum
                  slug:
                    type: string
                    example: museum
            count:
              type: integer
              example: 1
      400:
        description: Invalid language parameter
    """
    return get_all_venue_types()


@venue_types_bp.route("/<slug>", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_venue_type(slug):
    """
    Get single venue type by slug
    ---
    tags:
      - Venue Types
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Venue type slug
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
    responses:
      200:
        description: Venue type details
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
                  example: museum
                slug:
                  type: string
                  example: museum
      404:
        description: Venue type not found
    """
    return get_existing_venue_type(slug)


@venue_types_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def create_venue_type():
    """
    Create new venue type with auto-translation
    ---
    tags:
      - Venue Types
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: body
        name: body
        required: true
        description: At least one name in any supported language must be provided. Missing translations will be auto-generated.
        schema:
          type: object
          minProperties: 1
          properties:
            name_en:
              type: string
              description: English name (2-30 chars, lowercase)
              example: museum
            name_ru:
              type: string
              description: Russian name (2-30 chars, lowercase)
              example: музей
            name_he:
              type: string
              description: Hebrew name (2-30 chars)
              example: מוזיאון
    responses:
      201:
        description: Venue type created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Venue type created successfully
            data:
              type: object
              properties:
                name_ru:
                  type: string
                  example: музей
                name_en:
                  type: string
                  example: museum
                name_he:
                  type: string
                  example: מוזיאון
                slug:
                  type: string
                  example: museum
      400:
        description: Invalid input or no names provided
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      409:
        description: Venue type with this name already exists
    """
    return create_new_venue_type()


@venue_types_bp.route("/<slug>", methods=["PUT"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def full_update_venue_type(slug):
    """
    Full update of venue type
    ---
    tags:
      - Venue Types
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Venue type slug
      - in: body
        name: body
        required: true
        description: All names are required
        schema:
          type: object
          required:
            - name_en
            - name_ru
            - name_he
          properties:
            name_en:
              type: string
              description: English name (2-30 chars, lowercase)
              example: museum
            name_ru:
              type: string
              description: Russian name (2-30 chars, lowercase)
              example: музей
            name_he:
              type: string
              description: Hebrew name (2-30 chars)
              example: מוזיאון
    responses:
      200:
        description: Venue type updated successfully
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Venue type not found
    """
    return full_update_existing_venue_type(slug)


@venue_types_bp.route("/<slug>", methods=["PATCH"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def part_update_venue_type(slug):
    """
    Partial update of venue type
    ---
    tags:
      - Venue Types
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Venue type slug
      - in: body
        name: body
        required: true
        description: One or more names to update
        schema:
          type: object
          minProperties: 1
          properties:
            name_en:
              type: string
              description: English name (2-30 chars, lowercase)
              example: museum
            name_ru:
              type: string
              description: Russian name (2-30 chars, lowercase)
              example: музей
            name_he:
              type: string
              description: Hebrew name (2-30 chars)
              example: מוזיאון
    responses:
      200:
        description: Venue type partially updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: "Updated parameters: name_en. Unchanged parameters: name_ru, name_he"
            data:
              type: object
              properties:
                name_ru:
                  type: string
                  example: музей
                name_en:
                  type: string
                  example: museum
                name_he:
                  type: string
                  example: מוזיאון
                slug:
                  type: string
                  example: museum
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Venue type not found
    """
    return part_update_existing_venue_type(slug)


@venue_types_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def delete_venue_type(slug):
    """
    Delete venue type
    ---
    tags:
      - Venue Types
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Venue type slug
    responses:
      204:
        description: Venue type successfully deleted
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Venue type not found
      409:
        description: Cannot delete venue type with associated venues
    """
    return delete_existing_venue_type(slug)
