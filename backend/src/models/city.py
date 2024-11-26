from mongoengine import Document, StringField


class City(Document):
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
        "collection": "cities",
        "indexes": ["name_ru", "name_en", "name_he", "slug"]
    }

    def get_name(self, lang="en"):
        return getattr(self, f'name_{lang}')
