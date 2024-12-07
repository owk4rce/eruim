from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import public_routes_limit, protected_routes_limit
from backend.src.controllers.event_types_controller import get_all_event_types, create_new_event_type, \
    full_update_existing_event_type, part_update_existing_event_type, delete_existing_event_type, \
    get_existing_event_type
from backend.src.utils.custom_decorators import no_body_in_request, require_json, manager_required, no_args_in_request

# Create Blueprint for event types
event_types_bp = Blueprint("event_types", __name__, url_prefix="/event_types")


@event_types_bp.route("/", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_event_types():
    """
    Get list of all event types
    ---
    tags:
      - Event Types
    parameters:
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
    responses:
      200:
        description: List of event types
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
                    description: Event type name in requested language
                    example: concert
                  slug:
                    type: string
                    example: concert
            count:
              type: integer
              example: 1
      400:
        description: Invalid language parameter
    """
    return get_all_event_types()


@event_types_bp.route("/<slug>", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_event_type(slug):
    """
    Get single event type by slug
    ---
    tags:
      - Event Types
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Event type slug
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
    responses:
      200:
        description: Event type details
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
                  example: concert
                slug:
                  type: string
                  example: concert
      404:
        description: Event type not found
    """
    return get_existing_event_type(slug)


@event_types_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def create_event_type():
    """
    Create new event type with auto-translation
    ---
    tags:
      - Event Types
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
              description: English name (2-20 chars, lowercase)
              example: concert
            name_ru:
              type: string
              description: Russian name (2-20 chars, lowercase)
              example: концерт
            name_he:
              type: string
              description: Hebrew name (2-20 chars)
              example: קונצרט
    responses:
      201:
        description: Event type created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Event type created successfully
            data:
              type: object
              properties:
                name_ru:
                  type: string
                  example: концерт
                name_en:
                  type: string
                  example: concert
                name_he:
                  type: string
                  example: קונצרט
                slug:
                  type: string
                  example: concert
      400:
        description: Invalid input or no names provided
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      409:
        description: Event type with this name already exists
    """
    return create_new_event_type()


@event_types_bp.route("/<slug>", methods=["PUT"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def full_update_event_type(slug):
    """
    Full update of event type
    ---
    tags:
      - Event Types
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Event type slug
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
              description: English name (2-20 chars, lowercase)
              example: concert
            name_ru:
              type: string
              description: Russian name (2-20 chars, lowercase)
              example: концерт
            name_he:
              type: string
              description: Hebrew name (2-20 chars)
              example: קונצרט
    responses:
      200:
        description: Event type updated successfully
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Event type not found
    """
    return full_update_existing_event_type(slug)


@event_types_bp.route("/<slug>", methods=["PATCH"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def part_update_event_type(slug):
    """
    Partial update of event type
    ---
    tags:
      - Event Types
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Event type slug
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
              description: English name (2-20 chars, lowercase)
              example: concert
            name_ru:
              type: string
              description: Russian name (2-20 chars, lowercase)
              example: концерт
            name_he:
              type: string
              description: Hebrew name (2-20 chars)
              example: קונצרט
    responses:
      200:
        description: Event type partially updated successfully
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
                  example: концерт
                name_en:
                  type: string
                  example: concert
                name_he:
                  type: string
                  example: קונצרט
                slug:
                  type: string
                  example: concert
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Event type not found
    """
    return part_update_existing_event_type(slug)


@event_types_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def delete_event_type(slug):
    """
    Delete event type
    ---
    tags:
      - Event Types
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Event type slug
    responses:
      204:
        description: Event type successfully deleted
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Event type not found
      409:
        description: Cannot delete event type with associated events
    """
    return delete_existing_event_type(slug)
