from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import public_routes_limit, protected_routes_limit
from backend.src.controllers.venues_controllers import get_all_venues, create_new_venue, get_existing_venue, \
    full_update_existing_venue, part_update_existing_venue, delete_existing_venue
from backend.src.utils.custom_decorators import no_body_in_request, manager_required, no_args_in_request

# Create Blueprint for venues
venues_bp = Blueprint("venues", __name__, url_prefix="/venues")


@venues_bp.route("/", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_venues():
    """
    Get list of venues with filters
    ---
    tags:
      - Venues
    parameters:
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
      - in: query
        name: is_active
        type: string
        enum: [true, false]
        description: Filter by venue status
        required: false
      - in: query
        name: city
        type: string
        description: Filter by city slug
        required: false
    responses:
      200:
        description: List of venues
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                $ref: '#/definitions/VenueResponse'
            count:
              type: integer
              example: 1
      400:
        description: Invalid query parameters
    """
    return get_all_venues()


@venues_bp.route("/<slug>", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_venue(slug):
    """
    Get single venue by slug
    ---
    tags:
      - Venues
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Venue slug
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
    responses:
      200:
        description: Venue details
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              $ref: '#/definitions/VenueResponse'
      404:
        description: Venue not found
    """
    return get_existing_venue(slug)


@venues_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def create_venue():
    """
    Create new venue
    ---
    tags:
      - Venues
    security:
      - Bearer: []
      - Cookie: []
    consumes:
      - multipart/form-data
      - application/json
    parameters:
      - in: formData
        name: image
        type: file
        description: Venue image (PNG, JPG, JPEG, max 5MB)
        required: false
      - in: formData
        name: name_en
        type: string
        description: English name (3-100 chars)
        required: false
      - in: formData
        name: name_ru
        type: string
        description: Russian name (3-100 chars)
        required: false
      - in: formData
        name: name_he
        type: string
        description: Hebrew name (3-100 chars)
        required: false
      - in: formData
        name: address_en
        type: string
        description: English address (5-200 chars)
        required: true
      - in: formData
        name: city_en
        type: string
        description: English city name
        required: true
      - in: formData
        name: venue_type_en
        type: string
        description: English venue type name
        required: true
      - in: formData
        name: description_en
        type: string
        description: English description (20-1000 chars)
        required: false
      - in: formData
        name: description_ru
        type: string
        description: Russian description (20-1000 chars)
        required: false
      - in: formData
        name: description_he
        type: string
        description: Hebrew description (20-1000 chars)
        required: false
      - in: formData
        name: website
        type: string
        description: Website URL
        required: false
      - in: formData
        name: phone
        type: string
        description: Phone number (9-15 digits)
        required: false
      - in: formData
        name: email
        type: string
        format: email
        description: Contact email
        required: false
    responses:
      201:
        description: Venue created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Venue created successfully
            data:
              $ref: '#/definitions/VenueResponse'
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: City or venue type not found
      409:
        description: Venue with this name already exists
      415:
        description: Unsupported media type
    """
    return create_new_venue()


@venues_bp.route("/<slug>", methods=["PUT"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def full_update_venue(slug):
    """
    Full update of venue
    ---
    tags:
      - Venues
    security:
      - Bearer: []
      - Cookie: []
    consumes:
      - multipart/form-data
      - application/json
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Venue slug
      - in: formData
        name: image
        type: file
        description: New venue image
        required: false
      # Same parameters as in POST
      - in: formData
        name: is_active
        type: boolean
        required: true
        description: Venue status
    responses:
      200:
        description: Venue updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Venue fully updated successfully
            data:
              $ref: '#/definitions/VenueResponse'
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Venue, city or venue type not found
      409:
        description: Cannot deactivate venue with active events
      415:
        description: Unsupported media type
    """
    return full_update_existing_venue(slug)


@venues_bp.route("/<slug>", methods=["PATCH"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def part_update_venue(slug):
    """
    Partial update of venue
    ---
    tags:
      - Venues
    security:
      - Bearer: []
      - Cookie: []
    consumes:
      - multipart/form-data
      - application/json
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Venue slug
      - in: formData
        name: image
        type: file
        description: New venue image
        required: false
      # Any parameter from POST/PUT, all optional
    responses:
      200:
        description: Venue partially updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: "Updated parameters: name_en, description_en"
            data:
              $ref: '#/definitions/VenueResponse'
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Venue, city or venue type not found
      409:
        description: Cannot deactivate venue with active events
      415:
        description: Unsupported media type
    """
    return part_update_existing_venue(slug)


@venues_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def delete_venue(slug):
    """
    Delete venue
    ---
    tags:
      - Venues
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Venue slug
    responses:
      204:
        description: Venue successfully deleted
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Venue not found
      409:
        description: Cannot delete venue with active events
    """
    return delete_existing_venue(slug)
