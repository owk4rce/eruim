from dotenv import load_dotenv
import os
from datetime import timedelta
from backend.src.utils.exceptions import ConfigurationError


def load_config():
    """Load configuration from environment variables"""
    load_dotenv()

    # required env vars
    required_vars = {
        "DB_PATH",
        "DB_NAME",
        "GEONAMES_USERNAME",
        "HERE_API_KEY",
        "APP_SERVICE_EMAIL",
        "JWT_SECRET_KEY"
    }

    # get all keys as set
    env_vars = set(os.environ.keys())

    # looking for missing vars
    missing_vars = required_vars - env_vars

    if missing_vars:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return {
        # Database
        "DB_PATH": os.getenv("DB_PATH"),
        "DB_NAME": os.getenv("DB_NAME"),

        # JWT
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(days=1),
        "JWT_COOKIE_SECURE": True,

        # External APIs
        "GEONAMES_USERNAME": os.getenv("GEONAMES_USERNAME"),
        "HERE_API_KEY": os.getenv("HERE_API_KEY"),

        # Email
        "APP_SERVICE_EMAIL": os.getenv("APP_SERVICE_EMAIL"),

        # App settings
        "DEBUG": os.getenv("DEBUG", "False").lower() == "true",
        "MAX_FILE_SIZE": int(os.getenv("MAX_FILE_SIZE", 5_242_880))
    }