#from backend.src.config.db import db
from mongoengine import Document, StringField, ValidationError, DateTimeField, ReferenceField, DictField, URLField
from datetime import datetime


class Event(Document):
    name_ru = StringField(
        required=True,
        min_length=3,
        max_length=200,
        regex=r'^[а-яА-ЯёЁ\s-]+$',
        error_messages={
            'required': 'Russian event name is required',
            'min_length': 'Russian name must be at least 3 characters long',
            'max_length': 'Russian name cannot be longer than 200 characters',
            'regex': 'Only Russian letters, spaces and hyphens are allowed'
        }
    )

    name_en = StringField(
        required=True,
        min_length=3,
        max_length=200,
        regex=r'^[a-zA-Z\s-]+$',
        error_messages={
            'required': 'English event name is required',
            'min_length': 'English name must be at least 3 characters long',
            'max_length': 'English name cannot be longer than 200 characters',
            'regex': 'Only English letters, spaces and hyphens are allowed'
        }
    )

    name_he = StringField(
        required=True,
        min_length=3,
        max_length=200,
        regex=r'^[\u0590-\u05FF\s-]+$',
        error_messages={
            'required': 'Hebrew event name is required',
            'min_length': 'Hebrew name must be at least 3 characters long',
            'max_length': 'Hebrew name cannot be longer than 200 characters',
            'regex': 'Only Hebrew letters, spaces and hyphens are allowed'
        }
    )

    description_ru = StringField(
        required=True,
        min_length=20,
        max_length=2000,
        error_messages={
            'required': 'Russian description is required',
            'min_length': 'Russian description must be at least 20 characters long',
            'max_length': 'Russian description cannot be longer than 2000 characters'
        }
    )

    description_en = StringField(
        required=True,
        min_length=20,
        max_length=2000,
        error_messages={
            'required': 'English description is required',
            'min_length': 'English description must be at least 20 characters long',
            'max_length': 'English description cannot be longer than 2000 characters'
        }
    )

    description_he = StringField(
        required=True,
        min_length=20,
        max_length=2000,
        error_messages={
            'required': 'Hebrew description is required',
            'min_length': 'Hebrew description must be at least 20 characters long',
            'max_length': 'Hebrew description cannot be longer than 2000 characters'
        }
    )

    start_date = DateTimeField(
        required=True,
        error_messages={
            'required': 'Start date is required'
        }
    )

    end_date = DateTimeField(
        required=True,
        error_messages={
            'required': 'End date is required'
        }
    )

    venue = ReferenceField(
        'Venue',
        required=True,
        index=True,
        error_messages={
            'required': 'Venue reference is required'
        }
    )

    category = StringField(
        required=True,
        choices=['concert', 'theater', 'exhibition', 'festival', 'sport', 'other'],
        error_messages={
            'required': 'Category is required',
            'choices': 'Invalid category'
        }
    )

    status = StringField(
        required=True,
        choices=['draft', 'published', 'cancelled'],
        default='draft',
        error_messages={
            'choices': 'Invalid status'
        }
    )

    price_range = DictField(
        required=True,
        error_messages={
            'required': 'Price range is required'
        }
    )

    image_url = URLField(
        required=True,
        error_messages={
            'required': 'Image URL is required',
            'invalid': 'Invalid image URL format'
        }
    )

    meta = {
        'collection': 'events',
        'indexes': [
            "name_ru",
            "name_en",
            "name_he",
            'venue',
            'category',
            'start_date',
            'status'
        ]
    }

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError('End date must be after start date')

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}')

    def get_description(self, lang='en'):
        return getattr(self, f'description_{lang}')