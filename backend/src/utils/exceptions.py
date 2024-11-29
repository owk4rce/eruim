class ConfigurationError(Exception):
    """Raised when server configuration is invalid"""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code


class ExternalServiceError(Exception):
    """Raised when external service (API) fails"""
    def __init__(self, message, status_code=503):
        super().__init__(message)
        self.status_code = status_code


class UserError(Exception):
    """Base class for user-related errors that return 400 status code"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


class CityGeoNameError(Exception):
    """Raised when geocoding service fails"""
    pass


class CityValidationError(Exception):
    """Raised when city or alt names not found"""
    pass
