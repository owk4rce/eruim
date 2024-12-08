class ConfigurationError(Exception):
    """
    Raised when server configuration is invalid.

    Examples:
        - Missing required environment variables
        - Invalid database connection settings
        - Failed email service setup
    """
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code


class ExternalServiceError(Exception):
    """
    Raised when external service (API) fails.

    Examples:
        - GeoNames API errors
        - HERE Maps API errors
        - Google Translate API errors
    """
    def __init__(self, message, status_code=503):
        super().__init__(message)
        self.status_code = status_code


class UserError(Exception):
    """
    Base class for user-related errors that return 400 status code.

    Examples:
        - Invalid input data
        - Resource not found
        - Permission denied
        - Business logic violations
    """
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code