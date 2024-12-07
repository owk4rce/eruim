from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import protected_routes_limit
from backend.src.controllers.profile_controller import get_user_profile, full_update_user_profile, \
    part_update_user_profile, add_event_to_favorites, remove_event_from_favorites

from backend.src.utils.custom_decorators import no_body_in_request, no_args_in_request, require_json, \
    check_active_user

# Create Blueprint for venue types
profile_bp = Blueprint("profile", __name__, url_prefix="/users/me")


@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
@check_active_user()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def get_profile():
    """
    Get current user's profile
    ---
    tags:
      - Profile
    security:
      - Bearer: []
      - Cookie: []
    responses:
      200:
        description: User profile data
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                email:
                  type: string
                  format: email
                  example: user@example.com
                favorite_events:
                  type: array
                  description: List of favorite events in user's default language
                  items:
                    $ref: '#/definitions/EventResponse'
                default_lang:
                  type: string
                  enum: [en, ru, he]
                  example: en
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        description: Account is inactive
      404:
        description: User not found
    """
    return get_user_profile()


@profile_bp.route("/profile", methods=["PUT"])
@jwt_required()
@check_active_user()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def full_update_profile():
    """
    Full update of user profile
    ---
    tags:
      - Profile
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
            - email
            - password
            - default_lang
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              description: |
                Must contain:
                - At least 8 characters
                - English letters only (a-z, A-Z)
                - At least one uppercase letter
                - At least one lowercase letter
                - At least one number
                - At least one special character (@$!%*?&)
              example: StrongPass1!
            default_lang:
              type: string
              enum: [en, ru, he]
              example: en
    responses:
      200:
        description: Profile updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: User's profile fully updated successfully
            data:
              type: object
              properties:
                email:
                  type: string
                  format: email
                favorite_events:
                  type: array
                  items:
                    $ref: '#/definitions/EventResponse'
                default_lang:
                  type: string
                  enum: [en, ru, he]
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        description: Account is inactive
      404:
        description: User not found
    """
    return full_update_user_profile()


@profile_bp.route("/profile", methods=["PATCH"])
@jwt_required()
@check_active_user()
@protected_routes_limit()
@require_json()
@no_args_in_request()
def part_update_profile():
    """
    Partial update of user profile
    ---
    tags:
      - Profile
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: body
        name: body
        required: true
        description: One or more fields to update
        schema:
          type: object
          minProperties: 1
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              description: Requirements as in PUT request
              example: StrongPass1!
            default_lang:
              type: string
              enum: [en, ru, he]
              example: en
    responses:
      200:
        description: Profile partially updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: "Updated parameters: email. Unchanged parameters: default_lang"
            data:
              type: object
              properties:
                email:
                  type: string
                  format: email
                favorite_events:
                  type: array
                  items:
                    $ref: '#/definitions/EventResponse'
                default_lang:
                  type: string
                  enum: [en, ru, he]
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        description: Account is inactive
      404:
        description: User not found
    """
    return part_update_user_profile()


@profile_bp.route("/profile/fav/<event_slug>", methods=["POST"])
@jwt_required()
@check_active_user()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def add_to_favorites(event_slug):
    """
   Add event to favorites
    ---
    tags:
      - Profile
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: event_slug
        type: string
        required: true
        description: Event slug
    responses:
      200:
        description: Event added to favorites (or already in favorites)
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Event added to favorites
            data:
              type: object
              properties:
                email:
                  type: string
                  format: email
                favorite_events:
                  type: array
                  items:
                    $ref: '#/definitions/EventResponse'
                default_lang:
                  type: string
                  enum: [en, ru, he]
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        description: Account is inactive
      404:
        description: User or event not found
    """
    return add_event_to_favorites(event_slug)


@profile_bp.route("/profile/fav/<event_slug>", methods=["DELETE"])
@jwt_required()
@check_active_user()
@protected_routes_limit()
@no_body_in_request()
@no_args_in_request()
def remove_from_favorites(event_slug):
    """
    Remove event from favorites
    ---
    tags:
      - Profile
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: event_slug
        type: string
        required: true
        description: Event slug
    responses:
      200:
        description: Event removed from favorites (or wasn't in favorites)
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Event removed from favorites
            data:
              type: object
              properties:
                email:
                  type: string
                  format: email
                favorite_events:
                  type: array
                  items:
                    $ref: '#/definitions/EventResponse'
                default_lang:
                  type: string
                  enum: [en, ru, he]
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        description: Account is inactive
      404:
        description: User or event not found
    """
    return remove_event_from_favorites(event_slug)
