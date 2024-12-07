from mongoengine import Document, StringField, EmailField, ListField, ReferenceField, BooleanField, DateTimeField, \
    CASCADE
from datetime import datetime, timedelta
import bcrypt
import re
import pytz

from backend.src.utils.constants import SUPPORTED_LANGUAGES, TIMEZONE
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

    # reset password functionality
    reset_password_token = StringField(
        default=None
    )

    reset_password_token_created = DateTimeField(
        default=None
    )

    # account activation functionality
    email_confirmation_token = StringField(
        default=None
    )

    email_confirmation_token_created = DateTimeField(
        default=None
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
        if self.created_at:
            created_utc = pytz.utc.localize(self.created_at)
            created_local = created_utc.astimezone(TIMEZONE)
        else:
            created_local = None

        if self.last_login:
            last_login_utc = pytz.utc.localize(self.last_login)
            last_login_local = last_login_utc.astimezone(TIMEZONE)
        else:
            last_login_local = None

        return {
            "id": str(self.id),
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "favorite_events": [
                event.to_response_dict(self.default_lang) for event in self.favorite_events
            ],
            "default_lang": self.default_lang,
            "created_at": {
                "format": created_local.strftime('%d.%m.%Y %H:%M') if created_local else None,
                "local": created_local.strftime('%a, %d %b %Y %H:%M:%S %z') if created_local else None,
                "utc": self.created_at
            },
            "last_login": {
                "format": last_login_local.strftime('%d.%m.%Y %H:%M') if last_login_local else None,
                "local": last_login_local.strftime('%a, %d %b %Y %H:%M:%S %z') if last_login_local else None,
                "utc": self.last_login
            }
        }

    def to_profile_response_dict(self):
        """Convert user to API response format"""
        return {
            "email": self.email,
            "favorite_events": [
                event.to_response_dict(self.default_lang) for event in self.favorite_events
            ],
            "default_lang": self.default_lang
        }

    def set_reset_password_token(self, token):
        """Set reset password token and its creation time"""
        self.reset_password_token = token
        self.reset_password_token_created = datetime.utcnow()
        self.save()

    def clear_reset_password_token(self):
        """Clear reset password token and its creation time"""
        self.reset_password_token = None
        self.reset_password_token_created = None
        self.save()

    def is_reset_token_valid(self, token, expires_in=timedelta(hours=2)):
        """
        Check if reset password token is valid

        Args:
            token: Token to validate
            expires_in: Token lifetime, defaults to 24 hours

        Returns:
            bool: True if token is valid and not expired
        """
        if not self.reset_password_token or not self.reset_password_token_created:
            return False

        if self.reset_password_token != token:
            return False

        # check the validity time
        if datetime.utcnow() - self.reset_password_token_created > expires_in:
            return False

        return True

    #
    def set_email_confirmation_token(self, token):
        """Set reset password token and its creation time"""
        self.email_confirmation_token = token
        self.email_confirmation_token_created = datetime.utcnow()
        self.save()

    def clear_email_confirmation_token(self):
        """Clear reset password token and its creation time"""
        self.email_confirmation_token = None
        self.email_confirmation_token_created = None
        self.save()

    def is_confirmation_token_valid(self, token, expires_in=timedelta(hours=48)):
        """
        Check if reset password token is valid

        Args:
            token: Token to validate
            expires_in: Token lifetime, defaults to 24 hours

        Returns:
            bool: True if token is valid and not expired
        """
        if not self.email_confirmation_token or not self.email_confirmation_token_created:
            return False

        if self.email_confirmation_token != token:
            return False

        # check the validity time
        if datetime.utcnow() - self.email_confirmation_token_created > expires_in:
            return False

        return True
    #

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
