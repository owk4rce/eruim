from mongoengine import Document, StringField


class EventType(Document):
    """
    Represents a type/category of events with multilingual support.

    This model stores event type names in three languages (Russian, English, Hebrew)
    and a URL-friendly slug. Names are automatically converted to lowercase where applicable.

    Attributes:
        name_ru (str): Event type in Russian. Must contain only Russian letters, spaces, and hyphens.
            Automatically transformed to lowercase.
        name_en (str): Event type in English. Must contain only English letters, spaces, and hyphens.
            Automatically transformed to lowercase.
        name_he (str): Event type in Hebrew. Must contain only Hebrew letters, spaces, and hyphens.
        slug (str): URL-friendly version of the event type, usually generated from name_en.
            Must be unique across all event types.

    Validation Rules:
        - All names are required
        - Names length: 3-20 characters
        - Russian name: only а-яА-ЯёЁ characters plus space and hyphen
        - English name: only a-zA-Z characters plus space and hyphen
        - Hebrew name: only Hebrew characters plus space and hyphen
        - Slug: max 15 characters, must be unique, only lowercase letters, numbers and hyphens

    Example:
        >>> event_type = EventType(
        ...     name_en="Concert",
        ...     name_ru="Концерт",
        ...     name_he="קונצרט",
        ...     slug="concert"
        ... )
    """
    name_ru = StringField(
        required=True,
        min_length=3,
        max_length=20,
        regex=r'^[а-яА-ЯёЁ\s-]+$'
    )

    name_en = StringField(
        required=True,
        min_length=3,
        max_length=20,
        regex=r'^[a-zA-Z\s-]+$'
    )

    name_he = StringField(
        required=True,
        min_length=3,
        max_length=20,
        regex=r'^[\u0590-\u05FF\s-]+$'
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=15,
        regex=r'^[a-z0-9-]+$'
    )

    meta = {
        'collection': 'event_types',    # MongoDB collection name
        'indexes': ['name_ru', 'name_en', 'name_he', 'slug']    # Database indexes
    }

    def get_name(self, lang='en'):
        """
        Get event type name in specified language.

        Args:
            lang (str): Language code ('en', 'ru', or 'he'). Defaults to 'en'.

        Returns:
            str: Event type name in requested language.

        Example:
            >>> event_type = EventType(name_en="Concert", name_ru="Концерт", name_he="קונצרט")
            >>> event_type.get_name('ru')
            'концерт'
        """
        return getattr(self, f'name_{lang}')

    def to_response_dict(self):
        """Convert event type to API response format"""
        return {
            "name_ru": self.name_ru,
            "name_en": self.name_en,
            "name_he": self.name_he,
            "slug": self.slug
        }

    def clean(self):
        """Transform field values to lowercase before saving"""
        if self.name_en:
            self.name_en = self.name_en.lower()

        if self.name_ru:
            self.name_ru = self.name_ru.lower()
