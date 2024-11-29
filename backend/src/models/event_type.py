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
        regex=r'^[а-яА-ЯёЁ\s-]+$',
        transform=lambda x: x.lower() if x else x,  # always lowercase
        error_messages={
            'required': 'Russian type name is required',
            'min_length': 'Russian name must be at least 3 characters long',
            'max_length': 'Russian name cannot be longer than 20 characters',
            'regex': 'Only Russian letters, spaces and hyphens are allowed'
        }
    )

    name_en = StringField(
        required=True,
        min_length=3,
        max_length=20,
        regex=r'^[a-zA-Z\s-]+$',
        transform=lambda x: x.lower() if x else x,  # always lowercase
        error_messages={
            'required': 'English type name is required',
            'min_length': 'English name must be at least 3 characters long',
            'max_length': 'English name cannot be longer than 20 characters',
            'regex': 'Only English letters, spaces and hyphens are allowed'
        }
    )

    name_he = StringField(
        required=True,
        min_length=3,
        max_length=20,
        regex=r'^[\u0590-\u05FF\s-]+$',
        error_messages={
            'required': 'Hebrew type name is required',
            'min_length': 'Hebrew name must be at least 3 characters long',
            'max_length': 'Hebrew name cannot be longer than 20 characters',
            'regex': 'Only Hebrew letters, spaces and hyphens are allowed'
        }
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=15,
        regex=r'^[a-z0-9-]+$',
        error_messages={
            'required': 'Slug is required',
            'unique': 'This slug is already in use',
            'max_length': 'Slug cannot be longer than 15 characters',
            'regex': 'Only lowercase letters, numbers and hyphens are allowed'
        }
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
