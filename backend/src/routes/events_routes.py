from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import public_routes_limit, protected_routes_limit
from backend.src.controllers.events_controllers import get_all_events, get_existing_event, create_new_event, \
    full_update_existing_event, part_update_existing_event, delete_existing_event
from backend.src.utils.custom_decorators import no_body_in_request, manager_required, no_args_in_request

# Create Blueprint for events
events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.route("/", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_events():
    """
    Get list of events with filters
    ---
    tags:
      - Events
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
        description: Filter by event status
        required: false
      - in: query
        name: city
        type: string
        description: Filter by city slug (mutually exclusive with venue)
        required: false
      - in: query
        name: venue
        type: string
        description: Filter by venue slug (mutually exclusive with city)
        required: false
      - in: query
        name: sort
        type: string
        enum: [asc, desc]
        default: desc
        description: Sort by start date
        required: false
    responses:
      200:
        description: List of events
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                $ref: '#/definitions/EventResponse'
            count:
              type: integer
              example: 1
      400:
        description: Invalid query parameters
    """
    return get_all_events()


@events_bp.route("/<slug>", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def get_event(slug):
    """
   Get single event by slug
    ---
    tags:
      - Events
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Event slug
      - in: query
        name: lang
        type: string
        enum: [en, ru, he]
        description: Preferred language for response
        required: false
    responses:
      200:
        description: Event details
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              $ref: '#/definitions/EventResponse'
      404:
        description: Event not found
    """
    return get_existing_event(slug)


@events_bp.route("/", methods=["POST"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def create_event():
    """
    Create new event
    ---
    tags:
      - Events
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
        description: Event image (PNG, JPG, JPEG, max 5MB)
        required: false
      - in: formData
        name: name_en
        type: string
        description: English name (3-200 chars)
        required: false
      - in: formData
        name: name_ru
        type: string
        description: Russian name (3-200 chars)
        required: false
      - in: formData
        name: name_he
        type: string
        description: Hebrew name (3-200 chars)
        required: false
      - in: formData
        name: description_en
        type: string
        description: English description (20-2000 chars)
        required: false
      - in: formData
        name: description_ru
        type: string
        description: Russian description (20-2000 chars)
        required: false
      - in: formData
        name: description_he
        type: string
        description: Hebrew description (20-2000 chars)
        required: false
      - in: formData
        name: venue_slug
        type: string
        description: Venue slug
        required: true
      - in: formData
        name: event_type_slug
        type: string
        description: Event type slug
        required: true
      - in: formData
        name: start_date
        type: string
        description: Start date in format YYYY-MM-DD HH:MM or YYYY-MM-DD
        required: true
        example: "2024-12-31 19:00"
      - in: formData
        name: end_date
        type: string
        description: End date in format YYYY-MM-DD HH:MM or YYYY-MM-DD
        required: true
        example: "2024-12-31 23:00"
      - in: formData
        name: price_type
        type: string
        enum: [free, tba, fixed, starting_from]
        description: Price type
        required: true
      - in: formData
        name: price_amount
        type: integer
        description: Required for fixed and starting_from price types
        required: false
    responses:
      201:
        description: Event created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Event created successfully
            data:
              $ref: '#/definitions/EventResponse'
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Venue or event type not found
      409:
        description: Event with this name already exists
      415:
        description: Unsupported media type
    """
    return create_new_event()


@events_bp.route("/<slug>", methods=["PUT"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def full_update_event(slug):
    """
    Full update of event
    ---
    tags:
      - Events
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
        description: Event slug
      - in: formData
        name: image
        type: file
        description: New event image
        required: false
      # Same parameters as in POST route
    responses:
      200:
        description: Event updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Event updated successfully
            data:
              $ref: '#/definitions/EventResponse'
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Event, venue or event type not found
      415:
        description: Unsupported media type
    """
    return full_update_existing_event(slug)


@events_bp.route("/<slug>", methods=["PATCH"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_args_in_request()
def part_update_event(slug):
    """
    Partial update of event
    ---
    tags:
      - Events
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
        description: Event slug
      - in: formData
        name: image
        type: file
        description: New event image
        required: false
      # Any parameter from POST route, all optional
    responses:
      200:
        description: Event partially updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: "Updated parameters: name_en, price_type"
            data:
              $ref: '#/definitions/EventResponse'
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Event, venue or event type not found
      415:
        description: Unsupported media type
    """
    return part_update_existing_event(slug)


@events_bp.route("/<slug>", methods=["DELETE"])
@jwt_required()
@manager_required()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def delete_event(slug):
    """
    Delete event
    ---
    tags:
      - Events
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: slug
        type: string
        required: true
        description: Event slug
    responses:
      204:
        description: Event successfully deleted
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: Event not found
    """
    return delete_existing_event(slug)
