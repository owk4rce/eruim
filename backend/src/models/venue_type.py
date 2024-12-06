from mongoengine import Document, StringField


class VenueType(Document):
    """

    """
    name_ru = StringField(
        required=True,
        unique=True,
        min_length=2,
        max_length=30,
        regex=r'^[а-яё\s-]+$'
    )

    name_en = StringField(
        required=True,
        unique=True,
        min_length=2,
        max_length=30,
        regex=r'^[a-z\s-]+$'
    )

    name_he = StringField(
        required=True,
        unique=True,
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
