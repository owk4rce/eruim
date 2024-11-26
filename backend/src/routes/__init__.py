from flask import Blueprint
from .cities_routes import cities_bp

# Create a blueprint for API v1
api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Register routes for API v1
api_v1_bp.register_blueprint(cities_bp)
