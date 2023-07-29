import uuid
import phonenumbers
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from farmer.models import Farmer
from django.utils import timezone

from users.validators import validate_phonenumber
from utils.helpers import BaseModel

# Create your models here.


class VendorManager(models.Manager):

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


class Vendor(BaseModel):

    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)

    company_name = models.CharField(_("Company Name"), max_length=255)
    concerned_person = models.CharField(_("Concerned Person"), max_length=255, null=True, blank=True)
    date_of_joining = models.DateField(_("Date of joining"))

    profile_image = models.ImageField(
        _("Profile image"), upload_to='vendor/profile_image')

    SPINNING_VENDOR = 'SPINNING_VENDOR'
    GINNING_VENDOR = 'GINNING_VENDOR'
    ROLE_CHOICES = [
        (SPINNING_VENDOR, 'Spinning Vendor'),
        (GINNING_VENDOR, 'Ginning Vendor'),
    ]

    role = models.CharField(verbose_name=_(
        "Role (Ginning/Spinning)"), max_length=50, choices=ROLE_CHOICES)

    email = models.EmailField(
        _('Email Address'), unique=True, null=True, blank=True)

    phone = models.CharField(verbose_name=_("Phone Number"),
                             validators=[validate_phonenumber], max_length=17, unique=True)
    ID_TYPE_CHOICES = [
        ('AADHAR_CARD', 'Aadhar Card'),
        ('PAN_CARD', 'Pan Card'),
        ('DRIVERS_LICENSE', 'Drivers License'),
        ('OTHER', 'Other'),
    ]
    identification_type = models.CharField(verbose_name=_(
        "Identification Type"), max_length=100, choices=ID_TYPE_CHOICES, null=True, blank=True)
    identification_number = models.IntegerField(
        verbose_name=_("Identification Number"), null=True, blank=True)
    identification_file = models.FileField(verbose_name=_(
        "Identification File"), upload_to='vendor/identification', null=True, blank=True)

    website = models.URLField(verbose_name=_("Website"), null=True, blank=True)

    address = models.CharField(verbose_name=_("Address"), max_length=200)
    city = models.CharField(verbose_name=_("City"), max_length=200)
    state = models.CharField(verbose_name=_("State"), max_length=200)
    pincode = models.IntegerField(verbose_name=_("Pincode"))

    objects = VendorManager()

    def __str__(self):
        return self.user_display_name

    @property
    def user_display_name(self):
        return self.first_name + " " + self.last_name if self.last_name else self.first_name


class SelectedGinningFarmer(BaseModel):
    farmer_name = models.CharField(verbose_name=_(
        "Farmer Name"), max_length=200, null=True, blank=True)
    farmer = models.ForeignKey(
        Farmer, related_name="ginning_farmer", on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.IntegerField(verbose_name=_("Quantity"), )


class GinningMapping(BaseModel):
    vendor = models.ForeignKey(Vendor, verbose_name=_(
        "Vendor"), on_delete=models.CASCADE)
    selected_farmers = models.ManyToManyField(SelectedGinningFarmer, verbose_name=_(
        "Selected farmers"), related_name="ginning_mapping")

    UNDEFINED = 'Undefined'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (UNDEFINED, UNDEFINED),
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
    ]
    status = models.CharField(
        _("Status"), max_length=100, choices=STATUS_CHOICES, default=UNDEFINED)
    created_on = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    returned_quantity = models.IntegerField(
        _("Returned quantity"), null=True, blank=True)

    @property
    def total_quantity(self):
        quantity = 0
        for selected_farmer in self.selected_farmers.all():
            quantity += selected_farmer.quantity

        return quantity
