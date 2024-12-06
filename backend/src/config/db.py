from mongoengine import connect

from backend.src.utils.exceptions import ConfigurationError
# from backend.src.config.logger import logger


def connect_db(app):
    """

    """
    try:
        db_name = app.config["DB_NAME"]

        db_path = app.config["DB_PATH"]

        if not db_path.startswith(("mongodb://", "mongodb+srv://")):
            raise ConfigurationError("Invalid MongoDB URL format. Must start with 'mongodb://' or 'mongodb+srv://'")

        connection = connect(db=db_name, host=db_path)
        print("Connected to MongoDB")  # log

        return connection
    except Exception as e:
        error_message = f"Database connection failed: {str(e)}"
        print(error_message)
        raise ConfigurationError(error_message)
