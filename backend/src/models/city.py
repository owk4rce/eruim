from mongoengine import Document, StringField


class City(Document):
    """
    Represents a city in the system with multilingual support.

    This model stores city names in three languages (Russian, English, Hebrew)
    and a URL-friendly slug. All names must be unique across the system.

    Attributes:
        name_ru (str): City name in Russian. Must contain only Russian letters, spaces, and hyphens.
        name_en (str): City name in English. Must contain only English letters, spaces, and hyphens.
        name_he (str): City name in Hebrew. Must contain only Hebrew letters, spaces, and hyphens.
        slug (str): URL-friendly version of the city name, usually generated from name_en.

    Validation Rules:
        - All names are required and must be unique
        - Names length: 3-50 characters
        - Russian name: only а-яА-ЯёЁ characters plus space and hyphen
        - English name: only a-zA-Z characters plus space and hyphen
        - Hebrew name: only Hebrew characters plus space and hyphen
        - Slug: max 50 characters, must be unique

    Example:
        >>> city = City(
        ...     name_en="Jerusalem",
        ...     name_ru="Иерусалим",
        ...     name_he="ירושלים",
        ...     slug="jerusalem"
        ... )
    """
    name_ru = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=50,
        regex=r"^[а-яА-ЯёЁ\s-]+$",
        error_messages={
            "required": "Russian city name is required",
            "unique": "City with this Russian name already exists",
            "min_length": "Russian city name must be at least 3 characters long",
            "max_length": "Russian city name cannot be longer than 50 characters",
            "regex": "Only Russian letters, spaces and hyphens are allowed"
        }
    )
    name_en = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=50,
        regex=r"^[a-zA-Z\s-]+$",
        error_messages={
            "required": "English city name is required",
            "unique": "City with this English name already exists",
            "min_length": "English city name must be at least 3 characters long",
            "max_length": "English city name cannot be longer than 50 characters",
            "regex": "Only English letters, spaces and hyphens are allowed"
        }
    )
    name_he = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=50,
        regex=r"^[\u0590-\u05FF\s-]+$",
        error_messages={
            "required": "Hebrew city name is required",
            "unique": "City with this Hebrew name already exists",
            "min_length": "Hebrew city name must be at least 3 characters long",
            "max_length": "Hebrew city name cannot be longer than 50 characters",
            "regex": "Only Hebrew letters, spaces and hyphens are allowed"
        }
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=50,
        error_messages={
            'required': 'Slug is required',
            'unique': 'This slug is already in use',
            'max_length': 'Slug cannot be longer than 50 characters'
        }
    )

    meta = {
        "collection": "cities",  # MongoDB collection name
        "indexes": ["name_ru", "name_en", "name_he", "slug"]  # Database indexes
    }

    def get_name(self, lang="en"):
        """
        Get city name in specified language.

        Args:
            lang (str): Language code ('en', 'ru', or 'he'). Defaults to 'en'.

        Returns:
            str: City name in requested language.

        Example:
            >>> city = City(name_en="Jerusalem", name_ru="Иерусалим", name_he="ירושלים")
            >>> city.get_name("ru")
            'Иерусалим'
        """
        return getattr(self, f"name_{lang}")
