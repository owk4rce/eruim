from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.src.config.limiter import auth_limit, public_routes_limit
from backend.src.controllers.auth_controllers import register_new_user, existing_user_login, user_logout, \
    request_password_reset, verify_reset_token, confirm_password_reset, verify_email_confirmation_token
from backend.src.utils.custom_decorators import require_json, no_args_in_request, no_body_in_request

# Create Blueprint for authorization
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
@public_routes_limit()
@require_json()
@no_args_in_request()
def register_user():
    """
    Register new user account
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
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
              default: en
              example: en
    responses:
      201:
        description: Registration successful, activation email sent
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Registration successful. The activation email sent.
            data:
              type: object
              properties:
                id:
                  type: string
                email:
                  type: string
                role:
                  type: string
                  enum: [user]
                  example: user
                is_active:
                  type: boolean
                  example: false
                favorite_events:
                  type: array
                  items:
                    type: object
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
      409:
        description: User with this email already exists
    """
    return register_new_user()


@auth_bp.route("/login", methods=["POST"])
@auth_limit()
@require_json()
@no_args_in_request()
def user_login():
    """
    Login user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              example: StrongPass1!
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Login successful.
            data:
              type: object
              properties:
                id:
                  type: string
                email:
                  type: string
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
        description: Invalid email or password
      403:
        description: Account is inactive
    """
    return existing_user_login()


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
@no_body_in_request()
@no_args_in_request()
def logout():
    """
    Logout user
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
      - Cookie: []
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Logout successful.
      401:
        $ref: '#/responses/UnauthorizedError'
    """
    return user_logout()


@auth_bp.route("/reset-password/request", methods=["POST"])
@auth_limit()
@require_json()
@no_args_in_request()
def request_pwd_reset():
    """
    Request password reset
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              format: email
              example: user@example.com
    responses:
      200:
        description: Reset instructions sent if email exists
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: If the email exists, reset instructions will be sent.
    """
    return request_password_reset()


@auth_bp.route("/reset-password/verify", methods=["GET"])
@auth_limit()
@no_body_in_request()
def verify_token():
    """
    Verify reset password token
    ---
    tags:
      - Authentication
    parameters:
      - in: query
        name: token
        type: string
        required: true
        description: Reset token from email
    responses:
      200:
        description: Token is valid
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Token is valid.
      400:
        description: Reset token is missing or invalid
    """
    return verify_reset_token()


@auth_bp.route("/reset-password/confirm", methods=["POST"])
@auth_limit()
@require_json()
@no_args_in_request()
def reset_password_confirm():
    """
    Set new password using reset token
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - token
            - new_password
          properties:
            token:
              type: string
              description: Reset token from email
            new_password:
              type: string
              description: |
                Must contain:
                - At least 8 characters
                - English letters only (a-z, A-Z)
                - At least one uppercase letter
                - At least one lowercase letter
                - At least one number
                - At least one special character (@$!%*?&)
              example: NewStrongPass1!
    responses:
      200:
        description: Password reset successful
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Password has been reset successfully.
      400:
        description: Invalid token or password
    """
    return confirm_password_reset()


@auth_bp.route("/confirm_email/verify", methods=["GET"])
@public_routes_limit()
@no_body_in_request()
def verify_activation_token():
    """
    Verify email confirmation token
    ---
    tags:
      - Authentication
    parameters:
      - in: query
        name: token
        type: string
        required: true
        description: Activation token from email
    responses:
      200:
        description: Email confirmed, account activated
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Token is valid. Account is active.
      400:
        description: Activation token is missing or invalid
    """
    return verify_email_confirmation_token()