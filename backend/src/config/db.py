from mongoengine import connect
import logging

from backend.src.utils.exceptions import ConfigurationError


def connect_db(app):
    """

    """
    logger = logging.getLogger('backend')

    try:
        db_name = app.config["DB_NAME"]

        db_path = app.config["DB_PATH"]

        if not db_path.startswith(("mongodb://", "mongodb+srv://")):
            raise ConfigurationError("Invalid MongoDB URL format. Must start with 'mongodb://' or 'mongodb+srv://'")

        connection = connect(db=db_name, host=db_path)
        logger.info("Successfully connected to MongoDB.")

        return connection
    except Exception as e:
        error_message = f"Database connection failed: {str(e)}"
        print(error_message)
        raise ConfigurationError(error_message)
