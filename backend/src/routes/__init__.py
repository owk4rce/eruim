from flask import Blueprint

from .cities_routes import cities_bp
from .event_types_routes import event_types_bp
from .users_routes import users_bp
from .venue_types_routes import venue_types_bp
from .venues_routes import venues_bp
from .auth_routes import auth_bp

# Create a blueprint for API v1
api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Register routes for API v1
api_v1_bp.register_blueprint(cities_bp)
api_v1_bp.register_blueprint(event_types_bp)
api_v1_bp.register_blueprint(venue_types_bp)
api_v1_bp.register_blueprint(venues_bp)
api_v1_bp.register_blueprint(users_bp)
api_v1_bp.register_blueprint(auth_bp)
