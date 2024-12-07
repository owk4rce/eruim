from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.controllers.users_controller import get_all_users, get_existing_user, create_new_user, \
    full_update_existing_user, part_update_existing_user, delete_existing_user
from backend.src.utils.custom_decorators import admin_required, no_body_in_request, no_args_in_request, require_json

# Create Blueprint for venue types
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required()
@no_body_in_request()
def get_users():
    """
    Get list of all users (Admin only)
    ---
    tags:
      - Users Management
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: query
        name: is_active
        type: string
        enum: [true, false]
        description: Filter by user status
        required: false
      - in: query
        name: role
        type: string
        enum: [admin, manager, user]
        description: Filter by user role
        required: false
    responses:
      200:
        description: List of users
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
                  id:
                    type: string
                    example: "507f1f77bcf86cd799439011"
                  email:
                    type: string
                    format: email
                    example: manager@example.com
                  role:
                    type: string
                    enum: [admin, manager, user]
                  is_active:
                    type: boolean
                  favorite_events:
                    type: array
                    items:
                      $ref: '#/definitions/EventResponse'
                  default_lang:
                    type: string
                    enum: [en, ru, he]
                  created_at:
                    type: object
                    properties:
                      format:
                        type: string
                        example: "01.12.2023 12:00"
                      local:
                        type: string
                      utc:
                        type: string
                  last_login:
                    type: object
                    properties:
                      format:
                        type: string
                      local:
                        type: string
                      utc:
                        type: string
            count:
              type: integer
              example: 1
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
    """
    return get_all_users()


@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
@admin_required()
@no_body_in_request()
@no_args_in_request()
def get_user(user_id):
    """
    Get single user by ID (Admin only)
    ---
    tags:
      - Users Management
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: User ID
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                id:
                  type: string
                  example: "507f1f77bcf86cd799439011"
                email:
                  type: string
                  format: email
                  example: manager@example.com
                role:
                  type: string
                  enum: [admin, manager, user]
                is_active:
                  type: boolean
                favorite_events:
                  type: array
                  items:
                    $ref: '#/definitions/EventResponse'
                default_lang:
                  type: string
                  enum: [en, ru, he]
                created_at:
                  type: object
                  properties:
                    format:
                      type: string
                      example: "01.12.2023 12:00"
                    local:
                      type: string
                    utc:
                      type: string
                last_login:
                  type: object
                  properties:
                    format:
                      type: string
                    local:
                      type: string
                    utc:
                      type: string
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: User not found
    """
    return get_existing_user(user_id)


@users_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required()
@require_json()
@no_args_in_request()
def create_user():
    """
    Create new user (Admin only)
    ---
    tags:
      - Users Management
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
            - role
          properties:
            email:
              type: string
              format: email
              example: manager@example.com
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
            role:
              type: string
              enum: [admin, manager, user]
              example: manager
            is_active:
              type: boolean
              default: true
              example: true
            default_lang:
              type: string
              enum: [en, ru, he]
              default: en
              example: en
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: User created successfully
            data:
              type: object
              properties:
                id:
                  type: string
                email:
                  type: string
                  format: email
                role:
                  type: string
                  enum: [admin, manager, user]
                is_active:
                  type: boolean
                favorite_events:
                  type: array
                  items:
                    $ref: '#/definitions/EventResponse'
                default_lang:
                  type: string
                  enum: [en, ru, he]
                created_at:
                  type: object
                  properties:
                    format:
                      type: string
                    local:
                      type: string
                    utc:
                      type: string
                last_login:
                  type: object
                  properties:
                    format:
                      type: string
                    local:
                      type: string
                    utc:
                      type: string
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      409:
        description: User with this email already exists
    """
    return create_new_user()


@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
@admin_required()
@require_json()
@no_args_in_request()
def full_update_user(user_id):
    """
    Full update of user (Admin only)
    ---
    tags:
      - Users Management
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: User ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - role
            - is_active
            - default_lang
          properties:
            email:
              type: string
              format: email
            password:
              type: string
              description: Requirements as in POST request
            role:
              type: string
              enum: [admin, manager, user]
            is_active:
              type: boolean
            default_lang:
              type: string
              enum: [en, ru, he]
    responses:
      200:
        description: User updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: User fully updated successfully
            data:
              type: object
              # Same as in GET response
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: User not found
    """
    return full_update_existing_user(user_id)


@users_bp.route("/<user_id>", methods=["PATCH"])
@jwt_required()
@admin_required()
@require_json()
@no_args_in_request()
def part_update_user(user_id):
    """
    Partial update of user (Admin only)
    ---
    tags:
      - Users Management
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: User ID
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
            password:
              type: string
              description: Requirements as in POST request
            role:
              type: string
              enum: [admin, manager, user]
            is_active:
              type: boolean
            default_lang:
              type: string
              enum: [en, ru, he]
    responses:
      200:
        description: User partially updated successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: "Updated fields: role, is_active. Unchanged fields: email, default_lang"
            data:
              type: object
              # Same as in GET response
      400:
        description: Invalid input data
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: User not found
    """
    return part_update_existing_user(user_id)


@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@admin_required()
@no_body_in_request()
@no_args_in_request()
def delete_user(user_id):
    """
    Delete user (Admin only)
    ---
    tags:
      - Users Management
    security:
      - Bearer: []
      - Cookie: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: User ID
    responses:
      204:
        description: User successfully deleted
      401:
        $ref: '#/responses/UnauthorizedError'
      403:
        $ref: '#/responses/ForbiddenError'
      404:
        description: User not found
    """
    return delete_existing_user(user_id)
