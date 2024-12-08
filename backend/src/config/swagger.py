"""
Swagger/OpenAPI configuration for API documentation
"""

template = {
    "info": {
        "title": "Eruim: Cultural Events API",
        "description": """
        API for managing cultural events and venues in Israel.
        
        ## Authentication
        This API supports two authentication methods:
        1. Bearer Token in Authorization header
        2. HTTP-only cookie named 'token'
        
        Both methods use the same JWT token format.
        """,
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
        },
        "Cookie": {
            "type": "apiKey",
            "name": "token",
            "in": "cookie",
            "description": "JWT token in HTTP-only cookie. Set automatically after login."
        }
    },
    "security": [
        {"Bearer": []},
        {"Cookie": []}
    ],
    # Common responses that can be referenced from any route
    "responses": {
        "UnauthorizedError": {
            "description": "Authentication is required or token has expired",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Authentication required."
                    },
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        "ForbiddenError": {
            "description": "Insufficient permissions or inactive account",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Manager access required"
                    },
                    "message": {
                        "type": "string"
                    }
                }
            }
        }
    },
    # Common schemas that can be referenced from any route
    "definitions": {
        "VenueResponse": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "example": "Haifa Museum of Art"
                },
                "address": {
                    "type": "string",
                    "example": "26 Shabtai Levi St."
                },
                "description": {
                    "type": "string"
                },
                "venue_type": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "example": "museum"
                        },
                        "slug": {
                            "type": "string",
                            "example": "museum"
                        }
                    }
                },
                "city": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "example": "Haifa"
                        },
                        "slug": {
                            "type": "string",
                            "example": "haifa"
                        }
                    }
                },
                "location": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "example": "Point"
                        },
                        "coordinates": {
                            "type": "array",
                            "items": {"type": "number"},
                            "example": [34.989571, 32.819280]
                        }
                    }
                },
                "website": {
                    "type": "string",
                    "example": "https://www.hma.org.il"
                },
                "phone": {
                    "type": "string",
                    "example": "+972-4-852-1576"
                },
                "email": {
                    "type": "string",
                    "example": "info@hma.org.il"
                },
                "is_active": {
                    "type": "boolean"
                },
                "image_path": {
                    "type": "string"
                },
                "slug": {
                    "type": "string",
                    "example": "haifa-museum-of-art"
                }
            }
        },
        "EventResponse": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "example": "Jazz Concert"
                },
                "description": {
                    "type": "string"
                },
                "time": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "object",
                            "properties": {
                                "format": {
                                    "type": "string",
                                    "example": "31.12.2024 19:00"
                                },
                                "local": {
                                    "type": "string",
                                    "example": "Tue, 31 Dec 2024 19:00:00 +0200"
                                },
                                "utc": {
                                    "type": "string"
                                }
                            }
                        },
                        "end": {
                            "type": "object",
                            "properties": {
                                "format": {
                                    "type": "string",
                                    "example": "31.12.2024 23:00"
                                },
                                "local": {
                                    "type": "string",
                                    "example": "Tue, 31 Dec 2024 23:00:00 +0200"
                                },
                                "utc": {
                                    "type": "string"
                                }
                            }
                        },
                        "format": {
                            "type": "string",
                            "example": "19:00 - 23:00"
                        }
                    }
                },
                "venue": {
                    "$ref": "#/definitions/VenueResponse"
                },
                "event_type": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "example": "concert"
                        },
                        "slug": {
                            "type": "string",
                            "example": "concert"
                        }
                    }
                },
                "price": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["free", "tba", "fixed", "starting_from"]
                        },
                        "amount": {
                            "type": "integer",
                            "example": 100
                        },
                        "format": {
                            "type": "string",
                            "example": "100 ₪"
                        }
                    }
                },
                "is_active": {
                    "type": "boolean"
                },
                "image_path": {
                    "type": "string"
                },
                "slug": {
                    "type": "string",
                    "example": "jazz-concert-2024-12-31-19-00"
                }
            }
        }
    }
}


def get_swagger_config():
    """
    Get Swagger UI configuration settings
    """
    return {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/api/v1/apispec.json',
                "rule_filter": lambda rule: True,  # include all routes
                "model_filter": lambda tag: True,  # include all models
            }
        ],
        "static_url_path": "/api/v1/flaggger_static",
        "swagger_ui": True,
        "specs_route": "/api/v1/docs"
    }


def get_swagger_template():
    """
    Get Swagger API documentation template
    """
    return template
