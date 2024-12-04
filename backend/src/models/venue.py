from mongoengine import Document, StringField, ReferenceField, PointField, URLField, BooleanField, EmailField


class Venue(Document):
    """
       Represents a venue/location where events take place with multilingual support.

       This model stores venue details including names, addresses, descriptions in three languages
       (Russian, English, Hebrew), as well as location coordinates, contact information and other
       venue-specific attributes.

       Attributes:
           name_ru (str): Venue name in Russian. Must contain only Russian letters, spaces, and hyphens.
           name_en (str): Venue name in English. Must contain only English letters, spaces, and hyphens.
           name_he (str): Venue name in Hebrew. Must contain only Hebrew letters, spaces, and hyphens.
           address_ru (str): Physical address in Russian, 5-200 characters.
           address_en (str): Physical address in English, 5-200 characters.
           address_he (str): Physical address in Hebrew, 5-200 characters.
           description_ru (str): Venue description in Russian, 20-1000 characters.
           description_en (str): Venue description in English, 20-1000 characters.
           description_he (str): Venue description in Hebrew, 20-1000 characters.
           city (City): Reference to the City model where venue is located.
           location (tuple): GeoJSON point coordinates [longitude, latitude].
           website (str, optional): Venue's website URL.
           phone (str, optional): Contact phone number (9-15 digits, may start with +).
           email (str, optional): Contact email address.
           is_active (bool): Whether the venue is currently active. Defaults to True.
           image_path (str): Path to venue's image. Defaults to default.png.
           slug (str): URL-friendly version of the venue name. Must be unique.

       Validation Rules:
           - All names:
               - Required, 3-100 characters
               - Language-specific character sets
           - All addresses:
               - Required, 5-200 characters
           - All descriptions:
               - Required, 20-1000 characters
           - Location coordinates and city reference are required
           - Phone must match international format
           - Image path must follow specific pattern
           - Slug must be unique, max 100 characters

       Example:
           >>> venue = Venue(
           ...     name_en="Symphony Hall",
           ...     name_ru="Симфонический Зал",
           ...     name_he="היכל הסימפוניה",
           ...     address_en="123 Music Street, Jerusalem",
           ...     address_ru="улица Музыки 123, Иерусалим",
           ...     address_he="רחוב המוזיקה 123, ירושלים",
           ...     description_en="A premier concert venue...",
           ...     city=city_obj,
           ...     location=[34.781769, 32.085300],
           ...     slug="symphony-hall"
           ... )
    """
    name_ru = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=100,
        regex=r'^[а-яА-ЯёЁ\s\-]+$'
    )

    name_en = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=100,
        regex=r'^[a-zA-Z\s\-]+$'
    )

    name_he = StringField(
        required=True,
        unique=True,
        min_length=3,
        max_length=100,
        regex=r'^[\u0590-\u05FF\s\-]+$'
    )

    address_ru = StringField(
        required=True,
        min_length=5,
        max_length=200,
        regex=r'^[а-яА-ЯёЁ\s\d,./\-]+$'
    )

    address_en = StringField(
        required=True,
        min_length=5,
        max_length=200,
        regex=r'^[a-zA-Z\s\d,./\-]+$'
    )

    address_he = StringField(
        required=True,
        min_length=5,
        max_length=200,
        regex=r'^[\u0590-\u05FF\s\d,./\-]+$'
    )

    description_ru = StringField(
        required=True,
        min_length=20,
        max_length=1000,
        regex=r'^[а-яА-ЯёЁ\s\d,./\-–—:;\'\"«»„“”!?()\[\]]+$'
    )

    description_en = StringField(
        required=True,
        min_length=20,
        max_length=1000,
        regex=r'^[a-zA-Z\s\d,./\-–—:;\'\"«»!?()\[\]]+$'
    )

    description_he = StringField(
        required=True,
        min_length=20,
        max_length=1000,
        regex=r'^[\u0590-\u05FF\s\d,./\-–—:;\'\"«»!?()\[\]]+$'
    )

    venue_type = ReferenceField(
        'VenueType',
        required=True
    )

    city = ReferenceField(
        'City',
        required=True
    )

    location = PointField(
        required=True
    )

    website = URLField(
    )

    phone = StringField(
        regex=r'^\+?1?\d{9,15}$'
    )

    email = EmailField(
    )

    is_active = BooleanField(default=True)

    image_path = StringField(
        required=True,
        default='/uploads/img/venues/default/default.png',
        regex=r'^/uploads/img/venues/[\w-]+/[\w-]+\.png$'
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=100
    )

    meta = {
        'collection': 'venues',  # MongoDB collection name
        "indexes": ["name_ru",
                    "name_en",
                    "name_he",
                    "venue_type",
                    "city",
                    "slug"]  # Database indexes
    }

    def get_name(self, lang="en"):
        """
           Get venue name in specified language.

           Args:
               lang (str): Language code ('en', 'ru', or 'he'). Defaults to 'en'.

           Returns:
               str: Venue name in requested language.
        """
        return getattr(self, f'name_{lang}')

    def get_address(self, lang="en"):
        """
           Get venue address in specified language.

           Args:
               lang (str): Language code ('en', 'ru', or 'he'). Defaults to 'en'.

           Returns:
               str: Venue address in requested language.
        """
        return getattr(self, f"address_{lang}")

    def get_description(self, lang="en"):
        """
           Get venue description in specified language.

           Args:
               lang (str): Language code ('en', 'ru', or 'he'). Defaults to 'en'.

           Returns:
               str: Venue description in requested language.
        """
        return getattr(self, f"description_{lang}")

    def to_response_dict(self, lang=None):
        """Convert venue to API response format"""
        if not lang:
            return {
                "name_ru": self.name_ru,
                "name_en": self.name_en,
                "name_he": self.name_he,
                "address_en": self.address_en,
                "address_he": self.address_he,
                "address_ru": self.address_ru,
                "description_en": self.description_en,
                "description_he": self.description_he,
                "description_ru": self.description_ru,
                "venue_type": self.venue_type.to_response_dict(),
                "city": self.city.to_response_dict(),
                "location": self.location,
                "website": self.website,
                "phone": self.phone,
                "email": self.email,
                "is_active": self.is_active,
                "image_path": self.image_path,
                "slug": self.slug
            }
        else:
            return {
                "name": self.get_name(lang),
                "address": self.get_address(lang),
                "description": self.get_description(lang),
                "venue_type": self.venue_type.to_response_dict(lang),
                "city": self.city.to_response_dict(lang),
                "location": self.location,
                "website": self.website,
                "phone": self.phone,
                "email": self.email,
                "is_active": self.is_active,
                "image_path": self.image_path,
                "slug": self.slug
            }
