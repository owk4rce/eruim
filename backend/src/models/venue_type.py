from mongoengine import Document, StringField


class VenueType(Document):
    """
    Represents a type of venue in the system with multilingual support.

    Used for categorizing venues into types like 'museum', 'theater', etc.
    Each type must be unique and have names in three languages.
    Auto-converts English and Russian names to lowercase before saving.

    Fields:
        name_ru (str): Name in Russian, 2-30 chars, only lowercase Russian letters with space/hyphen
        name_en (str): Name in English, 2-30 chars, only lowercase English letters with space/hyphen
        name_he (str): Name in Hebrew, 2-30 chars, only Hebrew letters with space/hyphen
        slug (str): URL-friendly version, max 30 chars, auto-generated from name_en

    Validation:
        - All names must be unique across the system
        - No special characters allowed except space and hyphen
        - Only appropriate alphabet characters for each language
        - Enforces lowercase for English and Russian names
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
        "collection": "venue_types",    # MongoDB collection name
        "indexes": ["name_ru", "name_en", "name_he", "slug"]    # Database indexes
    }

    def get_name(self, lang='en'):
        """
        Retrieves venue type name in specified language.
        Language code must be one of: en, ru, he
        """
        return getattr(self, f'name_{lang}')

    def to_response_dict(self, lang=None):
        """
        Converts venue type to API response format.
        If lang is specified, returns only the name in that language and slug.
        Otherwise returns all names and slug.
        """
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
        """
        Automatically transforms English and Russian names to lowercase
        before saving to ensure consistency across the system
        """
        if self.name_en:
            self.name_en = self.name_en.lower()

        if self.name_ru:
            self.name_ru = self.name_ru.lower()
