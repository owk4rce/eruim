from flask import jsonify, request
from werkzeug.exceptions import BadRequest
from mongoengine.errors import ValidationError, NotUniqueError
from backend.src.utils.exceptions import UserError, ConfigurationError

import logging
logger = logging.getLogger('backend')


def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        logger.warning(f"Bad Request: {str(error)}")
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format or empty request body.'
        }), 400

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle MongoEngine ValidationError"""
        logger.warning(f"MongoEngine Validation Error: {str(error)}")
        return jsonify({
            'status': 'error',
            'message': str(error)
        }), 400

    @app.errorhandler(NotUniqueError)
    def handle_not_unique_error(error):
        logger.warning(f"MongoEngine Not Unique Error: {str(error)}")
        return jsonify({
            'status': 'error',
            'message': 'Resource with this name already exists.'
        }), 409

    @app.errorhandler(UserError)
    def handle_user_error(error):
        logger.warning(f"User Error: {str(error)}")
        return jsonify({
            'status': 'error',
            'message': str(error)
        }), error.status_code

    @app.errorhandler(429)
    def handle_ratelimit_error(error):
        logger.warning(f"Rate limit exceeded - IP: {request.remote_addr}, "
                       f"Path: {request.path}, Method: {request.method}")
        return jsonify({
            'status': 'error',
            'message': str(error.description)
        }), 429

    @app.errorhandler(ConfigurationError)
    def handle_config_error(error):
        logger.critical(f"Configuration Error: {str(error)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal Server Error'
        }), 500

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        logger.warning(f"Method Not Allowed: {request.method} {request.path}")
        return jsonify({
            'status': 'error',
            'message': 'Method not allowed for this route'
        }), 405

    @app.errorhandler(404)
    def handle_not_found(error):
        logger.warning(f"Not Found: {request.method} {request.path}")
        return jsonify({
            'status': 'error',
            'message': 'Route not found'
        }), 404

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        logger.error(f"Unhandled Error: {str(error)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal Server Error'
        }), 500
