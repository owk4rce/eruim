from mongoengine import Document, StringField


class EventType(Document):
    """

    """
    name_ru = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=20,
        regex=r'^[а-яё\s-]+$'
    )

    name_en = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=20,
        regex=r'^[a-z\s-]+$'
    )

    name_he = StringField(
        required=True,
        unique=True,
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
        "collection": "event_types",    # MongoDB collection name
        "indexes": ["name_ru", "name_en", "name_he", "slug"]    # Database indexes
    }

    def get_name(self, lang="en"):
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
        return getattr(self, f"name_{lang}")

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
