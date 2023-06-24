import uuid

import phonenumbers
import pytz
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from .utils import get_username
from .validators import validate_phonenumber

# Create your models here.


class UserManager(BaseUserManager):

    def normalize_email(self, email):
        if email:
            email = email.strip().lower()
        return email

    def normalize_phone(self, phone):
        if phone:
            phone = phone.strip().lower()
            phone_number = phonenumbers.parse(phone)
            phone = phonenumbers.format_number(
                phone_number, phonenumbers.PhoneNumberFormat.E164)
        return phone

    def create_user(self, username, password=None, email=None, phone=None, first_name=None, last_name=None, role=None):
        if not role:
            role = User.UNDEFINED
        email = self.normalize_email(email)
        phone = self.normalize_phone(phone)
        user = self.model(username=username,
                          email=email,
                          phone=phone,
                          first_name=first_name,
                          last_name=last_name,
                          role=role)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, email=None, phone=None, first_name=None, last_name=None, role=None):
        role = User.SUPER_USER
        user = self.create_user(username, password, email, phone, first_name, last_name, role)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
    

class User(AbstractUser):
    """
    Custom User has fields First Name, Last Name, Email Address,
    Phone Number, and Role in the website
    """
    class Meta:
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['username']),
            models.Index(fields=['user_display_name']),
        ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    first_name = models.CharField(_('first name'), max_length=150, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, null=True, blank=True)
    email = models.EmailField(
        _('Email Address'), unique=True, null=True, blank=True)
    phone = models.CharField(
        validators=[validate_phonenumber], max_length=17, unique=True, null=True, blank=True)
    SUPER_USER = 'SU'
    FARMER = 'CO'
    ADMIN = 'AD'
    UNDEFINED = 'UD'
    ROLE_CHOICES = [
        (SUPER_USER, 'Super User'),
        (FARMER, 'Farmer User'),
        (ADMIN, 'Admin user'),
    ]
    role = models.CharField(
        max_length=2, choices=ROLE_CHOICES, default=UNDEFINED,)
    TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(
        max_length=100, choices=TIMEZONE_CHOICES, default='Asia/Kolkata',
    )
    user_display_name = models.CharField(max_length=255, null=True, blank=True)
    history = HistoricalRecords()
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.user_display_name

    def save(self, *args, **kwargs):
        if self.role != self.SUPER_USER and self.role != self.UNDEFINED:
            self.username = get_username(self)
        self.user_display_name = user_display(self)
        super(User, self).save(*args, **kwargs)


def user_display(user):
    """
    The way a user's name is displayed.
    Standard format is 'First-Name Last-Name' or if no Last-Name,
    'First-Name'. In case of Name not provided,
    returns 'Username'
    """
    firstname = user.first_name
    space = " " if user.last_name else ""
    lastname = user.last_name
    name = f'{firstname}{space}{lastname}' if firstname else user.username
    return name
