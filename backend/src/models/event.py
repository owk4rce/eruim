from mongoengine import Document, StringField, ValidationError, DateTimeField, ReferenceField, IntField, BooleanField
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

    event_type = ReferenceField(
        'EventType',
        required=True,
        index=True,
        error_messages={
            'required': 'Event type reference is required'
        }
    )

    is_active = BooleanField(
        default=True
    )

    price_type = StringField(
        required=True,
        choices=['free', 'tba', 'fixed', 'starting_from'],
        error_messages={
            'required': 'Price type is required',
            'choices': 'Invalid price type'
        }
    )

    price_amount = IntField(
        min_value=0,
        error_messages={
            'min_value': 'Price amount cannot be negative'
        }
    )

    image_path = StringField(
        required=True,
        regex=r'^/static/img/events/[\w-]+/[\w-]+\.png$',
        error_messages={
            'required': 'Image path is required',
            'regex': 'Invalid image path format. Should be /static/img/events/event-slug/event-slug.png'
        }
    )

    meta = {
        'collection': 'events',
        'indexes': [
            "name_ru",
            "name_en",
            "name_he",
            'venue',
            'event_type',
            'start_date',
            'is_active'
        ]
    }

    def clean(self):
        """Validate event dates and price logic"""
        if self.end_date < self.start_date:
            raise ValidationError('End date must be after start date')

        # Validate price logic
        if self.price_type in ['fixed', 'starting_from']:
            if self.price_amount is None:
                raise ValidationError('Price amount is required for fixed and starting_from price types')
        elif self.price_type in ['free', 'tba']:
            if self.price_amount is not None:
                raise ValidationError('Price amount should not be set for free or TBA events')

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}')

    def get_description(self, lang='en'):
        return getattr(self, f'description_{lang}')

    @property
    def is_single_day_event(self):
        """Check if event starts and ends on the same day"""
        return self.start_date.date() == self.end_date.date()

    def get_formatted_time(self):
        """Get formatted time string based on event type"""
        if self.is_single_day_event:
            return f"{self.start_date.strftime('%H:%M')} - {self.end_date.strftime('%H:%M')}"
        else:
            return f"{self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')}"