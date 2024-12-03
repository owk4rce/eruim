from mongoengine import Document, StringField, EmailField, ListField, ReferenceField, BooleanField, DateTimeField, \
    CASCADE
from datetime import datetime
import bcrypt
import re
from backend.src.utils.constants import SUPPORTED_LANGUAGES
from backend.src.utils.exceptions import UserError


class User(Document):
    """
    User model with role-based access control

    Roles:
    - admin: Full access to all features
    - manager: Can manage events, cities, and venues
    - user: Basic user with favorites functionality
    """
    email = EmailField(
        required=True,
        unique=True
    )

    password = StringField(
        required=True
    )

    role = StringField(
        required=True,
        choices=["admin", "manager", "user"],
        default="user"
    )

    is_active = BooleanField(
        default=True
    )

    favorite_events = ListField(
        ReferenceField("Event", reverse_delete_rule=CASCADE),
        default=list
    )

    default_lang = StringField(
        required=True,
        choices=SUPPORTED_LANGUAGES,  # ['en', 'ru', 'he']
        default="en"
    )

    created_at = DateTimeField(
        default=datetime.utcnow
    )

    last_login = DateTimeField(
        default=None
    )

    meta = {
        "collection": "users",
        "indexes": [
            "email",
            "role",
            "is_active"
        ]
    }

    def validate_password(self, password):
        """
        Validate password against requirements:
        - English letters only
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character from @$!%*?&
        """
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(password_pattern, password):
            raise UserError(
                'Password requirements: '
                'At least 8 characters long. '
                'Only English letters (a-z, A-Z). '
                'At least one uppercase letter. '
                'At least one lowercase letter. '
                'At least one number. '
                'At least one special character (@$!%*?&)'
            )
        return True

    def verify_password(self, password):
        """Verify password against stored hash"""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password.encode("utf-8")
        )

    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role

    def is_admin(self):
        """Check if user is admin"""
        return self.role == "admin"

    def is_manager(self):
        """Check if user is manager"""
        return self.role == "manager"

    def can_manage_content(self):
        """Check if user can manage content (admin or manager)"""
        return self.role in ["admin", "manager"]

    def add_to_favorites(self, event):
        """Add event to favorites if not already present"""
        if event not in self.favorite_events:
            self.favorite_events.append(event)
            self.save()

    def remove_from_favorites(self, event):
        """Remove event from favorites if present"""
        if event in self.favorite_events:
            self.favorite_events.remove(event)
            self.save()

    def to_response_dict(self):
        """Convert event type to API response format"""
        return {
            "id": str(self.id),
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "favorite_events": [
                event.to_response_dict(self.default_lang) for event in self.favorite_events
            ],
            "created_at": self.created_at,
            "last_login": self.last_login
        }

    def clean(self):
        """Validate and hash password before saving"""
        if self._data.get('password'):
            if not self.id or self._get_changed_fields().count('password'):
                # First validate the password
                self.validate_password(self.password)
                # If validation passes, hash the password
                self.password = bcrypt.hashpw(
                    self.password.encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
