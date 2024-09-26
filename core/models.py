from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import re

# Create your models here.


class UserManager(BaseUserManager):
    """User manager"""

    def create_user(self, mobile, password=None, **extra_fields):
        """Validates, creates, and saves a new user"""

        if not password or not re.match(
            r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password
        ):
            raise ValueError(
                [
                    'User must have a valid password',
                    'password must contain at least 8 characters',
                    'at least one alphabet',
                    'at least one digit',
                    'and at least one special character',
                ]
            )

        if not extra_fields.get('email'):
            raise ValueError('User must have an email address')

        if not re.match(
            r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            extra_fields.get('email')
        ):
            raise ValueError('User must have a valid email address')
        extra_fields['email'] = self.normalize_email(extra_fields['email'])

        username = extra_fields.get('username')
        if not username:
            raise ValueError('User must have a username')
        username = username.strip().lower()

        if not re.match(
            r'^[a-zA-Z]{5,20}$', username
        ):
            raise ValueError([
                'Username must contain only alphabetical characters',
                'and must be between 5 and 20 characters long'
            ])
        extra_fields['username'] = username

        if not mobile:
            raise ValueError('User must have a mobile number')
        if not re.match(r'^[0-9]{10}$', mobile):
            raise ValueError('User must have a valid mobile number')

        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password, **extra_fields):
        """Creates and saves a new superuser"""

        user = self.create_user(mobile, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports login
    using mobile instead of username
    """
    # choices for profile_type
    class ProfileType(models.TextChoices):
        """Profile type choices"""
        DEVELOPER = 'DEVELOPER', _("Developer")

    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=10, unique=True)
    username = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_type = models.CharField(
        max_length=64, choices=ProfileType.choices, default=ProfileType.DEVELOPER
    )
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile']

    def __str__(self):
        return str(self.username)

    class Meta:
        ordering = ['username']
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

