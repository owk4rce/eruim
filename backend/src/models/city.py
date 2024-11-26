from requests import get, RequestException
from slugify import slugify
from mongoengine import Document, StringField, ValidationError
import os



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

    # def clean(self):
    #     """
    #     Custom validation using GeoNames API
    #     """
    #     # Only validate if this is a new document or name_en has changed
    #     if self._created or self._get_changed_fields().get('name_en'):
    #         try:
    #             names = self.validate_and_get_names(self.name_en)
    #             print(names)
    #             # Update names if they're different
    #             if self.name_ru != names['ru']:
    #                 self.name_ru = names['ru']
    #             if self.name_he != names['he']:
    #                 self.name_he = names['he']
    #
    #             if not self.slug:
    #                 self.slug = slugify(self.name_en)
    #
    #         except ValidationError as e:
    #             raise ValidationError(f"City validation failed: {str(e)}")
