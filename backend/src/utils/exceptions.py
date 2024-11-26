class ConfigurationError(Exception):
    """Raised when server configuration is invalid"""
    pass


class CityGeoNameError(Exception):
    """Raised when geocoding service fails"""
    pass


class CityValidationError(Exception):
    """Raised when city or alt names not found"""
    pass
