from mongoengine import connect
import logging

from backend.src.utils.exceptions import ConfigurationError

logger = logging.getLogger('backend')


def connect_db(app):
    """
    Connect to MongoDB using configuration from Flask app.

    Args:
        app: Flask application instance with config containing DB_NAME and DB_PATH

    Returns:
        mongoengine.connection: Database connection object

    Raises:
        ConfigurationError: If connection fails or MongoDB URL is invalid
    """
    try:
        db_name = app.config["DB_NAME"]

        db_path = app.config["DB_PATH"]

        if not db_path.startswith(("mongodb://", "mongodb+srv://")):
            raise ConfigurationError("Invalid MongoDB URL format. Must start with 'mongodb://' or 'mongodb+srv://'")

        connection = connect(db=db_name, host=db_path)
        logger.info("Successfully connected to MongoDB.")

        return connection
    except Exception as e:
        raise ConfigurationError(f"Database connection failed: {str(e)}")
