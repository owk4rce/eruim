from mongoengine import Document, StringField, EmailField, ListField, ReferenceField, BooleanField, DateTimeField
from datetime import datetime
import bcrypt
import re
from mongoengine.errors import ValidationError


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
        unique=True,
        error_messages={
            'required': 'Email is required',
            'unique': 'User with this email already exists'
        }
    )

    password = StringField(
        required=True,
        error_messages={
            'required': 'Password is required'
        }
    )

    role = StringField(
        required=True,
        choices=['admin', 'manager', 'user'],
        default='user',
        error_messages={
            'choices': 'Invalid role'
        }
    )

    is_active = BooleanField(
        default=True
    )

    favorite_events = ListField(
        ReferenceField('Event'),
        default=list
    )

    created_at = DateTimeField(
        default=datetime.utcnow
    )

    last_login = DateTimeField(
        default=datetime.utcnow
    )

    meta = {
        'collection': 'users',
        'indexes': [
            'email',
            'role',
            'is_active'
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
            raise ValidationError(
                'Password requirements: \n'
                '- At least 8 characters long\n'
                '- Only English letters (a-z, A-Z)\n'
                '- At least one uppercase letter\n'
                '- At least one lowercase letter\n'
                '- At least one number\n'
                '- At least one special character (@$!%*?&)'
            )
        return True

    def clean(self):
        """Validate and hash password before saving"""
        if self._data.get('password') and self._get_changed_fields().count('password'):
            # First validate the password
            self.validate_password(self.password)
            # If validation passes, hash the password
            self.password = bcrypt.hashpw(
                self.password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

    def verify_password(self, password):
        """Verify password against stored hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password.encode('utf-8')
        )

    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role

    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

    def is_manager(self):
        """Check if user is manager"""
        return self.role == 'manager'

    def can_manage_content(self):
        """Check if user can manage content (admin or manager)"""
        return self.role in ['admin', 'manager']

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