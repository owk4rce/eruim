from flask import Blueprint
from backend.src.controllers.event_types_controller import get_all_event_types, create_new_event_type

# Create Blueprint for event types
event_types_bp = Blueprint("event_types", __name__, url_prefix="/event_types")


@event_types_bp.route("/", methods=["GET"])
def get_event_types():
    """Handle GET request for retrieving all event types"""
    return get_all_event_types()


@event_types_bp.route("/", methods=["POST"])
def create_event_type():
    """Handle POST request for creating new event type"""
    return create_new_event_type()

