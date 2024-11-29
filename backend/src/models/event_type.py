from mongoengine import Document, StringField


class EventType(Document):
    name_ru = StringField(
        required=True,
        min_length=3,
        max_length=20,
        regex=r'^[а-яА-ЯёЁ\s-]+$',
        transform=lambda x: x.lower() if x else x,  # always lowercase
        error_messages={
            'required': 'Russian type name is required',
            'min_length': 'Russian name must be at least 3 characters long',
            'max_length': 'Russian name cannot be longer than 20 characters',
            'regex': 'Only Russian letters, spaces and hyphens are allowed'
        }
    )

    name_en = StringField(
        required=True,
        min_length=3,
        max_length=20,
        regex=r'^[a-zA-Z\s-]+$',
        transform=lambda x: x.lower() if x else x,  # always lowercase
        error_messages={
            'required': 'English type name is required',
            'min_length': 'English name must be at least 3 characters long',
            'max_length': 'English name cannot be longer than 20 characters',
            'regex': 'Only English letters, spaces and hyphens are allowed'
        }
    )

    name_he = StringField(
        required=True,
        min_length=3,
        max_length=20,
        regex=r'^[\u0590-\u05FF\s-]+$',
        error_messages={
            'required': 'Hebrew type name is required',
            'min_length': 'Hebrew name must be at least 3 characters long',
            'max_length': 'Hebrew name cannot be longer than 20 characters',
            'regex': 'Only Hebrew letters, spaces and hyphens are allowed'
        }
    )

    slug = StringField(
        required=True,
        unique=True,
        max_length=15,
        regex=r'^[a-z0-9-]+$',
        error_messages={
            'required': 'Slug is required',
            'unique': 'This slug is already in use',
            'max_length': 'Slug cannot be longer than 15 characters',
            'regex': 'Only lowercase letters, numbers and hyphens are allowed'
        }
    )

    meta = {
        'collection': 'event_types',
        'indexes': ['name_ru', 'name_en', 'name_he', 'slug']
    }

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}')
