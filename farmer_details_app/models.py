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
        _("Profile image"), upload_to='vendor/profile_image', default="farmer_profile_image/blank-profile-picture.png")

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
        ('AADHAR_CARD', 'Aadhar card-Registration certification'),
        ('PAN_CARD', 'Pan Card'),
        ('DRIVERS_LICENSE', 'Factory license-Driving license'),
        ('OTHER', 'Other'),
    ]
    identification_type = models.CharField(verbose_name=_(
        "Identification Type"), max_length=100, choices=ID_TYPE_CHOICES, null=True, blank=True)
    identification_number = models.CharField(
        verbose_name=_("Identification Number"),max_length=255, null=True, blank=True)
    identification_file = models.FileField(verbose_name=_(
        "Identification File"), upload_to='vendor/identification', null=True, blank=True)

    website = models.URLField(verbose_name=_("Website"), null=True, blank=True)

    address = models.CharField(verbose_name=_("Address"), max_length=200)
    city = models.CharField(verbose_name=_("City"), max_length=200)
    state = models.CharField(verbose_name=_("State"), max_length=200)
    pincode = models.PositiveBigIntegerField(verbose_name=_("Pincode"))

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
    quantity = models.FloatField(verbose_name=_("Quantity"), validators = [MinValueValidator(0.0)])


class Ginning(BaseModel):
    vendor = models.ForeignKey(Vendor, verbose_name=_(
        "Vendor"), on_delete=models.CASCADE)
    selected_farmers = models.ManyToManyField(SelectedGinningFarmer, verbose_name=_(
        "Selected farmers"), related_name="ginning_mapping")

    timestamp = models.DateTimeField(auto_now_add=True)
    total_quantity = models.FloatField(validators = [MinValueValidator(0.0)])
    
    def save(self, *args, **kwargs):
        self.total_quantity = 0
        for selected_farmer in self.selected_farmers.all():
            self.total_quantity += selected_farmer.quantity
        super(Ginning, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.vendor} | {self.timestamp.date()}"
    
    # @property
    # def total_quantity(self):
    #     quantity = 0
    #     for selected_farmer in self.selected_farmers.all():
    #         quantity += selected_farmer.quantity

    #     return quantity
    
    
class GinningStatus(BaseModel):
    ginning = models.OneToOneField(Ginning, related_name="ginning_status", on_delete=models.PROTECT)

    UNDEFINED = 'Undefined'
    IN_PROGRESS = 'In Progress'
    QC_PENDING = 'QC Pending'
    QC_APPROVED = 'QC Approved'
    QC_REJECTED = 'QC Rejected'
    COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (UNDEFINED, UNDEFINED),
        (IN_PROGRESS, IN_PROGRESS),
        (QC_PENDING, QC_PENDING),
        (QC_APPROVED, QC_APPROVED),
        (QC_REJECTED, QC_REJECTED),
        (COMPLETED, COMPLETED),
    ]
    
    status = models.CharField(
        _("Status"), max_length=100, choices=STATUS_CHOICES, default=IN_PROGRESS)
    remark = models.CharField(
        _("Status"), max_length=1000, null=True, blank=True)
    # quality = models.ForeignKey(
    #     Quality, related_name="ginning_status", on_delete=models.PROTECT, null=True, blank=True)
    # rejected_count = models.PositiveBigIntegerField(
    #     _("Number of times it got rejected"), default=0)


class GinningInbound(BaseModel):
    ginning = models.OneToOneField(Ginning, verbose_name=_(
        "Ginning"), related_name='ginning_inbound', on_delete=models.PROTECT)
    timestamp = models.DateTimeField(_("Timestamp"))
    quantity = models.FloatField(_("Inbound Quantity"), validators = [MinValueValidator(0.0)])
    rate = models.FloatField(_("Inbound Cost as per Invoice"), validators = [MinValueValidator(0.0)])
    invoice_details = models.CharField(_("Invoice Details"), max_length=500)

    def __str__(self):
        return f"{self.ginning} | {self.quantity}"



class SelectedGinning(BaseModel):
    ginning = models.ForeignKey(Ginning, verbose_name=_(
        "Ginning"), related_name="selected_ginnings", on_delete=models.PROTECT)
    quantity = models.FloatField(verbose_name=_("Quantity"), validators = [MinValueValidator(0.0)])

    
class Spinning(BaseModel):
    selected_ginnings = models.ManyToManyField(SelectedGinning, verbose_name=_(
        "Selected Ginnings"), related_name="spinnings")
    vendor = models.ForeignKey(Vendor, verbose_name=_(
        "Vendor"), on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def total_quantity(self):
        quantity = 0
        for selected_farmer in self.selected_ginnings.all():
            quantity += selected_farmer.quantity

        return quantity
    

class SpinningStatus(BaseModel):
    spinning = models.OneToOneField(Spinning, related_name="spinning_status", on_delete=models.PROTECT)

    UNDEFINED = 'Undefined'
    IN_PROGRESS = 'In Progress'
    QC_PENDING = 'QC Pending'
    QC_APPROVED = 'QC Approved'
    QC_REJECTED = 'QC Rejected'
    COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (UNDEFINED, UNDEFINED),
        (IN_PROGRESS, IN_PROGRESS),
        (QC_PENDING, QC_PENDING),
        (QC_APPROVED, QC_APPROVED),
        (QC_REJECTED, QC_REJECTED),
        (COMPLETED, COMPLETED),
    ]
    
    status = models.CharField(
        _("Status"), max_length=100, choices=STATUS_CHOICES, default=IN_PROGRESS)
    remark = models.CharField(
        _("Status"), max_length=1000, null=True, blank=True)
    # quality = models.ForeignKey(
    #     Quality, related_name="ginning_status", on_delete=models.PROTECT, null=True, blank=True)
    # rejected_count = models.PositiveBigIntegerField(
    #     _("Number of times it got rejected"), default=0)


class SpinningInbound(BaseModel):
    spinning = models.OneToOneField(Spinning, verbose_name=_(
        "Spinning"), related_name='spinning_inbound', on_delete=models.PROTECT)
    timestamp = models.DateTimeField(_("Timestamp"))
    quantity = models.FloatField(_("Inbound Quantity"), validators = [MinValueValidator(0.0)])
    rate = models.FloatField(_("Inbound Cost as per Invoice"), validators = [MinValueValidator(0.0)])
    invoice_details = models.CharField(_("Invoice Details"), max_length=500)

    def __str__(self):
        return f"{self.spinning} | {self.quantity}"

    