from mongoengine import Document, StringField


class VenueType(Document):
    """
    Represents a type/category of venues with multilingual support.

    This model stores venue type names in three languages (Russian, English, Hebrew)
    and a URL-friendly slug. Names are automatically converted to lowercase where applicable.

    Attributes:
        name_ru (str): Venue type in Russian. Must contain only Russian letters, spaces, and hyphens.
            Automatically transformed to lowercase.
        name_en (str): Venue type in English. Must contain only English letters, spaces, and hyphens.
            Automatically transformed to lowercase.
        name_he (str): Venue type in Hebrew. Must contain only Hebrew letters, spaces, and hyphens.
        slug (str): URL-friendly version of the venue type, usually generated from name_en.
            Must be unique across all venue types.

    Validation Rules:
        - All names are required
        - Names length: 2-30 characters
        - Russian name: only а-яА-ЯёЁ characters plus space and hyphen
        - English name: only a-zA-Z characters plus space and hyphen
        - Hebrew name: only Hebrew characters plus space and hyphen
        - Slug: max 30 characters, must be unique, only lowercase letters, numbers and hyphens

    Example:
        >>> venue_type = VenueType(
        ...     name_en="museum",
        ...     name_ru="музей",
        ...     name_he="מוזיאון",
        ...     slug="museum"
        ... )
    """
    name_ru = StringField(
        required=True,
        min_length=2,
        max_length=30,
        regex=r'^[а-яА-ЯёЁ\s\-]+$'
    )

    name_en = StringField(
        required=True,
        min_length=2,
        max_length=30,
        regex=r'^[a-zA-Z\s\-]+$'
    )

    name_he = StringField(
        required=True,
        min_length=2,
        max_length=30,
        regex=r'^[\u0590-\u05FF\s\-]+$'
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=30,
        regex=r'^[a-z0-9-]+$'
    )

    meta = {
        'collection': 'venue_types',    # MongoDB collection name
        'indexes': ['name_ru', 'name_en', 'name_he', 'slug']    # Database indexes
    }

    def get_name(self, lang='en'):
        """
        Get venue type name in specified language.

        Args:
            lang (str): Language code ('en', 'ru', or 'he'). Defaults to 'en'.

        Returns:
            str: Venue type name in requested language.

        Example:
            >>> venue_type = VenueType(name_en="museum", name_ru="музей", name_he="מוזיאון")
            >>> venue_type.get_name('ru')
            'музей'
        """
        return getattr(self, f'name_{lang}')

    def to_response_dict(self, lang=None):
        """Convert event type to API response format"""
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

    def clean(self):
        """Transform field values to lowercase before saving"""
        if self.name_en:
            self.name_en = self.name_en.lower()

        if self.name_ru:
            self.name_ru = self.name_ru.lower()
