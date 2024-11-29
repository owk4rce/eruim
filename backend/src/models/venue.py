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
        min_length=3,
        max_length=100,
        regex=r'^[а-яА-ЯёЁ\s-]+$',
        error_messages={
            'required': 'Russian venue name is required',
            'min_length': 'Russian venue name must be at least 3 characters long',
            'max_length': 'Russian venue name cannot be longer than 100 characters',
            'regex': 'Only Russian letters, spaces and hyphens are allowed'
        }
    )

    name_en = StringField(
        required=True,
        min_length=3,
        max_length=100,
        regex=r'^[a-zA-Z\s-]+$',
        error_messages={
            'required': 'English venue name is required',
            'min_length': 'English venue name must be at least 3 characters long',
            'max_length': 'English venue name cannot be longer than 100 characters',
            'regex': 'Only English letters, spaces and hyphens are allowed'
        }
    )

    name_he = StringField(
        required=True,
        min_length=3,
        max_length=100,
        regex=r'^[\u0590-\u05FF\s-]+$',
        error_messages={
            'required': 'Hebrew venue name is required',
            'min_length': 'Hebrew venue name must be at least 3 characters long',
            'max_length': 'Hebrew venue name cannot be longer than 100 characters',
            'regex': 'Only Hebrew letters, spaces and hyphens are allowed'
        }
    )

    address_ru = StringField(
        required=True,
        min_length=5,
        max_length=200,
        error_messages={
            'required': 'Russian address is required',
            'min_length': 'Russian address must be at least 5 characters long',
            'max_length': 'Russian address cannot be longer than 200 characters'
        }
    )

    address_en = StringField(
        required=True,
        min_length=5,
        max_length=200,
        error_messages={
            'required': 'English address is required',
            'min_length': 'English address must be at least 5 characters long',
            'max_length': 'English address cannot be longer than 200 characters'
        }
    )

    address_he = StringField(
        required=True,
        min_length=5,
        max_length=200,
        error_messages={
            'required': 'Hebrew address is required',
            'min_length': 'Hebrew address must be at least 5 characters long',
            'max_length': 'Hebrew address cannot be longer than 200 characters'
        }
    )

    description_ru = StringField(
        required=True,
        min_length=20,
        max_length=1000,
        error_messages={
            'required': 'Russian description is required',
            'min_length': 'Russian description must be at least 20 characters long',
            'max_length': 'Russian description cannot be longer than 1000 characters'
        }
    )

    description_en = StringField(
        required=True,
        min_length=20,
        max_length=1000,
        error_messages={
            'required': 'English description is required',
            'min_length': 'English description must be at least 20 characters long',
            'max_length': 'English description cannot be longer than 1000 characters'
        }
    )

    description_he = StringField(
        required=True,
        min_length=20,
        max_length=1000,
        error_messages={
            'required': 'Hebrew description is required',
            'min_length': 'Hebrew description must be at least 20 characters long',
            'max_length': 'Hebrew description cannot be longer than 1000 characters'
        }
    )

    city = ReferenceField(
        'City',
        required=True,
        index=True,
        error_messages={
            'required': 'City reference is required'
        }
    )

    location = PointField(
        required=True,
        error_messages={
            'required': 'Location coordinates are required'
        }
    )

    website = URLField(
        error_messages={
            'invalid': 'Invalid URL format'
        }
    )

    phone = StringField(
        regex=r'^\+?1?\d{9,15}$',
        error_messages={
            'regex': 'Invalid phone number format'
        }
    )

    email = EmailField(
        error_messages={
            'invalid': 'Invalid email format'
        }
    )

    is_active = BooleanField(default=True)

    image_path = StringField(
        required=True,
        default='/uploads/img/venues/default/default.png',
        regex=r'^/uploads/img/venues/[\w-]+/[\w-]+\.png$',
        error_messages={
            'required': 'Image path is required',
            'regex': 'Invalid image path format. Should be /uploads/img/venues/venue-slug/venue-slug.png'
        }
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=100,
        error_messages={
            'required': 'Slug is required',
            'unique': 'This slug is already in use',
            'max_length': 'Slug cannot be longer than 100 characters'
        }
    )

    meta = {
        'collection': 'venues',     # MongoDB collection name
        "indexes": ["name_ru", "name_en", "name_he", "slug"]    # Database indexes
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
