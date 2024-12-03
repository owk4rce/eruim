from mongoengine import connect
from backend.src.utils.exceptions import ConfigurationError


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
        error_message = f"Failed to connect to MongoDB: {str(e)}"
        print(error_message)  # log
        raise ConfigurationError(error_message)
