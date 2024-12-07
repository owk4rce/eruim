import pytz
from mongoengine import Document, StringField, ValidationError, DateTimeField, ReferenceField, IntField, BooleanField, \
    CASCADE
from datetime import datetime
from backend.src.utils.constants import PRICE_TYPE_TRANSLATIONS, TIMEZONE


class Event(Document):
    name_ru = StringField(
        required=True,
        min_length=3,
        max_length=200,
        regex=r'^[а-яА-ЯёЁ\d\s\-–—\'\"«»„":]+$'
    )

    name_en = StringField(
        required=True,
        min_length=3,
        max_length=200,
        regex=r'^[a-zA-Z\d\s\-–—\'\"«»:]+$'
    )

    name_he = StringField(
        required=True,
        min_length=3,
        max_length=200,
        regex=r'^[\u0590-\u05FF\d\s\-–—\'\"«»״׳:]+$'
    )

    description_ru = StringField(
        required=True,
        min_length=20,
        max_length=2000,
        regex=r'^[а-яА-ЯёЁ\d\s\-–—.,!?()\'\"«»„":\[\];]+$'
    )

    description_en = StringField(
        required=True,
        min_length=20,
        max_length=2000,
        regex=r'^[a-zA-Z\d\s\-–—.,!?()\'\"«»:\[\];]+$'
    )

    description_he = StringField(
        required=True,
        min_length=20,
        max_length=2000,
        regex=r'^[\u0590-\u05FF\d\s\-–—.,!?()\'\"«»״׳:\[\];]+$'
    )

    start_date = DateTimeField(
        required=True
    )

    end_date = DateTimeField(
        required=True
    )

    venue = ReferenceField(
        'Venue',
        required=True,
        reverse_delete_rule=CASCADE
    )

    event_type = ReferenceField(
        'EventType',
        required=True
    )

    is_active = BooleanField(
        default=True
    )

    price_type = StringField(
        required=True,
        choices=['free', 'tba', 'fixed', 'starting_from']
    )

    price_amount = IntField(
        min_value=0,
        default=None,
    )

    image_path = StringField(
        required=True,
        default='/uploads/img/events/default/default.png',
        regex=r'^/uploads/img/events/[\w-]+/[\w-]+\.png$'
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=100
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
            'is_active',
            "slug"
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

        start_local = pytz.utc.localize(self.start_date).astimezone(TIMEZONE)
        end_local = pytz.utc.localize(self.end_date).astimezone(TIMEZONE)

        if self.is_single_day_event:
            return f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}"
        else:
            return f"{start_local.strftime('%d.%m.%Y')} - {end_local.strftime('%d.%m.%Y')}"

    def _format_price(self, lang='en'):
        """Format price based on price_type in specified language"""
        price_name = PRICE_TYPE_TRANSLATIONS[self.price_type][lang]

        if self.price_type == 'free':
            return price_name
        elif self.price_type == 'tba':
            return price_name
        elif self.price_type == 'fixed':
            return f"{self.price_amount}₪"
        elif self.price_type == 'starting_from':
            return f"{price_name} {self.price_amount} ₪"

    def to_response_dict(self, lang=None):
        """Convert venue to API response format"""

        start_local = pytz.utc.localize(self.start_date).astimezone(TIMEZONE)
        end_local = pytz.utc.localize(self.end_date).astimezone(TIMEZONE)

        if not lang:
            return {
                "name_ru": self.name_ru,
                "name_en": self.name_en,
                "name_he": self.name_he,
                "description_en": self.description_en,
                "description_he": self.description_he,
                "description_ru": self.description_ru,
                "time": {
                    "start": {
                        "format": start_local.strftime('%d.%m.%Y %H:%M'),
                        "local": start_local.strftime('%a, %d %b %Y %H:%M:%S %z'),
                        "utc": self.start_date
                    },
                    "end": {
                        "format": end_local.strftime('%d.%m.%Y %H:%M'),
                        "local": end_local.strftime('%a, %d %b %Y %H:%M:%S %z'),
                        "utc": self.end_date
                    },
                    "format": self.get_formatted_time()
                },
                "venue": self.venue.to_response_dict(),
                "event_type": self.event_type.to_response_dict(),
                "price": {
                    "type": self.price_type,
                    "amount": self.price_amount,
                    "format": {
                        "en": self._format_price('en'),
                        "ru": self._format_price('ru'),
                        "he": self._format_price('he')
                    }
                },
                "is_active": self.is_active,
                "image_path": self.image_path,
                "slug": self.slug
            }
        else:
            return {
                "name": self.get_name(lang),
                "description": self.get_description(lang),
                "time": {
                    "start": {
                        "format": start_local.strftime('%d.%m.%Y %H:%M'),
                        "local": start_local.strftime('%a, %d %b %Y %H:%M:%S %z'),
                        "utc": self.start_date
                    },
                    "end": {
                        "format": end_local.strftime('%d.%m.%Y %H:%M'),
                        "local": end_local.strftime('%a, %d %b %Y %H:%M:%S %z'),
                        "utc": self.end_date
                    },
                    "format": self.get_formatted_time()
                },
                "venue": self.venue.to_response_dict(lang),
                "event_type": self.event_type.to_response_dict(lang),
                "price": {
                    "type": self.price_type,
                    "amount": self.price_amount,
                    "format": self._format_price(lang)
                },
                "is_active": self.is_active,
                "image_path": self.image_path,
                "slug": self.slug
            }
