from dotenv import load_dotenv
import os
from datetime import timedelta
from backend.src.utils.exceptions import ConfigurationError


def load_config():
    """
    Load application configuration from environment variables.

    Validates presence of required environment variables and returns config dict
    with database, JWT, API keys and application settings.

    Returns:
        dict: Application configuration settings

    Raises:
        ConfigurationError: If any required environment variables are missing
    """
    load_dotenv()

    # required env vars
    required_vars = {
        "DB_PATH",
        "DB_NAME",
        "GEONAMES_USERNAME",
        "HERE_API_KEY",
        "APP_SERVICE_EMAIL",
        "APP_SERVICE_EMAIL_PASSWORD",
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
        "JWT_COOKIE_SECURE": False if os.getenv("DEBUG") == "true" else True,
        "JWT_TOKEN_LOCATION": ["headers", "cookies"],  # looking for token in headers and cookies
        "JWT_ACCESS_COOKIE_NAME": "token",  # name of cookie
        "JWT_COOKIE_CSRF_PROTECT": False,

        # External APIs
        "GEONAMES_USERNAME": os.getenv("GEONAMES_USERNAME"),
        "HERE_API_KEY": os.getenv("HERE_API_KEY"),

        # Email
        "APP_SERVICE_EMAIL": os.getenv("APP_SERVICE_EMAIL"),
        "APP_SERVICE_EMAIL_PASSWORD": os.getenv("APP_SERVICE_EMAIL_PASSWORD"),
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": 587,

        # App URL
        "BASE_URL": os.getenv("BASE_URL", "http://localhost:5000"),

        # App settings
        "DEBUG": os.getenv("DEBUG", "False").lower() == "true",
        "MAX_FILE_SIZE": int(os.getenv("MAX_FILE_SIZE", 5_242_880))     # Default 5MB
    }