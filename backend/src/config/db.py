from mongoengine import connect
import os
from backend.src.utils.exceptions import ConfigurationError


def connect_db():
    """
    Establish connection to MongoDB using environment variables.

    This function attempts to connect to a MongoDB database using credentials
    stored in environment variables. It performs validation of the connection
    string format and ensures all required environment variables are present.

    Environment Variables Required:
        DB_NAME: Name of the database to connect to
        DB_PATH: MongoDB connection string (must start with mongodb:// or mongodb+srv://)

    Returns:
        MongoEngine connection object if successful

    Raises:
        ConfigurationError: If any of these conditions occur:
            - DB_NAME environment variable is not set
            - DB_PATH environment variable is not set
            - DB_PATH has invalid format
            - Connection to MongoDB fails
    """
    try:
        db_name = os.getenv("DB_NAME")

        if not db_name:
            raise ConfigurationError("DB_NAME not set in .env")

        db_path = os.getenv("DB_PATH")

        if not db_path:
            raise ConfigurationError("DB_PATH not set in .env")

        if not db_path.startswith(("mongodb://", "mongodb+srv://")):
            raise ConfigurationError("Invalid MongoDB URL format. Must start with 'mongodb://' or 'mongodb+srv://'")

        connection = connect(db=db_name, host=db_path)
        print("Connected to MongoDB")  # log

        return connection
    except Exception as e:
        error_message = f"Failed to connect to MongoDB: {str(e)}"
        print(error_message)  # log
        raise ConfigurationError(error_message)
