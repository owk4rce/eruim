from mongoengine import Document, StringField


class City(Document):
    """
    Represents a city in the system with multilingual support.

    This model stores city names in three languages (Russian, English, Hebrew)
    and a URL-friendly slug. All names must be unique across the system.

    Fields:
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
    """
    name_ru = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=50,
        regex=r"^[а-яА-ЯёЁ\s-]+$"
    )
    name_en = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=50,
        regex=r"^[a-zA-Z\s-]+$"
    )
    name_he = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=50,
        regex=r"^[\u0590-\u05FF\s-]+$"
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=50
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
        """
        return getattr(self, f"name_{lang}")

    def to_response_dict(self, lang=None):
        """
        Convert city to API response format.

        Args:
            lang (str, optional): If provided, returns single name in specified language.
                                Otherwise returns all names.

        Returns:
            dict: City data formatted for API response
        """
        if not lang:
            return {
                "name_ru": self.name_ru,
                "name_en": self.name_en,
                "name_he": self.name_he,
                "slug": self.slug
            }
        else:
            return {
                "name": self.get_name(lang),
                "slug": self.slug
            }
