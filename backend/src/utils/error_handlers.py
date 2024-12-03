from flask import jsonify
from werkzeug.exceptions import BadRequest
from mongoengine.errors import ValidationError, NotUniqueError
from backend.src.utils.exceptions import UserError, ConfigurationError


def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format or empty request body'
        }), 400

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle MongoEngine ValidationError"""
        return jsonify({
            'status': 'error',
            'message': str(error)
        }), 400

    @app.errorhandler(NotUniqueError)
    def handle_not_unique_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource with this name already exists'
        }), 409

    @app.errorhandler(UserError)
    def handle_user_error(error):
        return jsonify({
            'status': 'error',
            'message': str(error)
        }), error.status_code

    @app.errorhandler(ConfigurationError)
    def handle_config_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Server configuration error'
        }), 500

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            'status': 'error',
            'message': 'Method not allowed for this route'
        }), 405

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Route not found'
        }), 404

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        print(f"Unhandled error: {str(error)}")  # log for debugging
        return jsonify({
            'status': 'error',
            'message': 'Internal Server Error'
        }), 500
