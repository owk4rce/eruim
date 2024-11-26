from backend.src.config.db import db


class Venue(db.Document):
    name_ru = db.StringField(
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

    name_en = db.StringField(
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

    name_he = db.StringField(
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

    address_ru = db.StringField(
        required=True,
        min_length=5,
        max_length=200,
        error_messages={
            'required': 'Russian address is required',
            'min_length': 'Russian address must be at least 5 characters long',
            'max_length': 'Russian address cannot be longer than 200 characters'
        }
    )

    address_en = db.StringField(
        required=True,
        min_length=5,
        max_length=200,
        error_messages={
            'required': 'English address is required',
            'min_length': 'English address must be at least 5 characters long',
            'max_length': 'English address cannot be longer than 200 characters'
        }
    )

    address_he = db.StringField(
        required=True,
        min_length=5,
        max_length=200,
        error_messages={
            'required': 'Hebrew address is required',
            'min_length': 'Hebrew address must be at least 5 characters long',
            'max_length': 'Hebrew address cannot be longer than 200 characters'
        }
    )

    description_ru = db.StringField(
        required=True,
        min_length=20,
        max_length=1000,
        error_messages={
            'required': 'Russian description is required',
            'min_length': 'Russian description must be at least 20 characters long',
            'max_length': 'Russian description cannot be longer than 1000 characters'
        }
    )

    description_en = db.StringField(
        required=True,
        min_length=20,
        max_length=1000,
        error_messages={
            'required': 'English description is required',
            'min_length': 'English description must be at least 20 characters long',
            'max_length': 'English description cannot be longer than 1000 characters'
        }
    )

    description_he = db.StringField(
        required=True,
        min_length=20,
        max_length=1000,
        error_messages={
            'required': 'Hebrew description is required',
            'min_length': 'Hebrew description must be at least 20 characters long',
            'max_length': 'Hebrew description cannot be longer than 1000 characters'
        }
    )

    city = db.ReferenceField(
        'City',
        required=True,
        index=True,
        error_messages={
            'required': 'City reference is required'
        }
    )

    location = db.PointField(
        required=True,
        error_messages={
            'required': 'Location coordinates are required'
        }
    )

    website = db.URLField(
        error_messages={
            'invalid': 'Invalid URL format'
        }
    )

    phone = db.StringField(
        regex=r'^\+?1?\d{9,15}$',
        error_messages={
            'regex': 'Invalid phone number format'
        }
    )

    is_active = db.BooleanField(default=True)

    image_url = db.URLField(
        error_messages={
            'invalid': 'Invalid image URL format'
        }
    )

    slug = db.StringField(
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
        'collection': 'venues',
        "indexes": ["name_ru", "name_en", "name_he", "slug"]
    }

    def get_name(self, lang="en"):
        return getattr(self, f'name_{lang}')

    def get_address(self, lang="en"):
        return getattr(self, f"address_{lang}")

    def get_description(self, lang="en"):
        return getattr(self, f"description_{lang}")
