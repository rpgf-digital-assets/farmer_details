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
    price = models.FloatField(verbose_name=_("Price per Kg"), validators = [MinValueValidator(0.0)], default=0.0)
    slip_no = models.CharField(_("Slip No."), max_length=255, default="0")
    inward_lot_no = models.CharField(_("Inward Lot No."), max_length=255, default="0")


class Ginning(BaseModel):
    vendor = models.ForeignKey(Vendor, verbose_name=_(
        "Vendor"), on_delete=models.CASCADE)
    selected_farmers = models.ManyToManyField(SelectedGinningFarmer, verbose_name=_(
        "Selected farmers"), related_name="ginning_mapping")
    
    timestamp = models.DateTimeField(_("Date"), default=timezone.now)
    total_quantity = models.FloatField(validators = [MinValueValidator(0.0)])
    
    def save(self, *args, **kwargs):
        self.total_quantity = 0
        for selected_farmer in self.selected_farmers.all():
            self.total_quantity += selected_farmer.quantity
        super(Ginning, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.vendor} | {self.timestamp.date()}"

    
class GinningStatus(BaseModel):
    ginning = models.OneToOneField(Ginning, related_name="ginning_status", on_delete=models.PROTECT)

    UNDEFINED = 'Undefined'
    INBOUND = 'Inbound'
    IN_PROGRESS = 'In Progress'
    QC_PENDING = 'QC Pending'
    QC_APPROVED = 'QC Approved'
    QC_REJECTED = 'QC Rejected'
    COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (UNDEFINED, UNDEFINED),
        (INBOUND, INBOUND),
        (IN_PROGRESS, IN_PROGRESS),
        (QC_PENDING, QC_PENDING),
        (QC_APPROVED, QC_APPROVED),
        (QC_REJECTED, QC_REJECTED),
        (COMPLETED, COMPLETED),
    ]

    status = models.CharField(
        _("Status"), max_length=100, choices=STATUS_CHOICES, default=INBOUND)
    length = models.CharField(
        _("Length"), max_length=255, default="0")
    mic = models.CharField(
        _("Mic"), max_length=255, default="0")
    strength = models.CharField(
        _("strength"), max_length=255, default="0")
    trash = models.CharField(
        _("Trash"), max_length=255, default="0")
    rd_plus = models.CharField(
        _("Rd+"), max_length=255, default="0")


class GinningInProcess(BaseModel):
    ginning = models.OneToOneField(Ginning, verbose_name=_(
        "Ginning"), related_name='ginning_inprocess', on_delete=models.PROTECT)
    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now)
    name = models.CharField(_("Ginning Name"), max_length=500)
    heap_no = models.CharField(_("Heap No."), max_length=500)
    consumed_qty = models.FloatField(_("Consumed raw cotton Quantity (Kgs)"), validators = [MinValueValidator(0.0)])
    lint_qty = models.FloatField(_("Lint Quantity (Kgs)"), validators = [MinValueValidator(0.0)])
    recovery = models.FloatField(_("Recovery %"), validators = [MinValueValidator(0.0), MaxValueValidator(100.0)])
    
    def save(self, *args, **kwargs):
        self.recovery = (self.lint_qty / self.consumed_qty) * 100
        super(GinningInProcess, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.ginning} | {self.name}"


class GinningOutbound(BaseModel):
    ginning = models.OneToOneField(Ginning, verbose_name=_(
        "Ginning"), related_name='ginning_outbound', on_delete=models.PROTECT)
    timestamp = models.DateTimeField(_("Timestamp"))
    invoice_no = models.CharField(_("Invoice No."), max_length=500)
    product_name = models.CharField(_("Product Name"), max_length=500)
    outward_lot_no = models.CharField(_("Outward Lot No"), max_length=500)

    def __str__(self):
        return f"{self.ginning} | {self.quantity}"
    quantity = models.FloatField(_("Quantity (Kgs)"), validators = [MinValueValidator(0.0)])


class SelectedGinning(BaseModel):
    ginning = models.ForeignKey(Ginning, verbose_name=_(
        "Ginning"), related_name="selected_ginnings", on_delete=models.PROTECT)
    quantity = models.FloatField(verbose_name=_("Quantity"), validators = [MinValueValidator(0.0)])
    price = models.FloatField(verbose_name=_("Price Per Kg"), validators = [MinValueValidator(0.0)], default=0.0)
    invoice_no = models.CharField(_("Invoice No."), max_length=500, default="0")
    lot_no = models.CharField(_("Lot No"), max_length=500, default="0")
    lint_cotton_tc_no = models.CharField(_("Lint Cotton TC No."), max_length=500, default="0")
    
    
class Spinning(BaseModel):
    selected_ginnings = models.ManyToManyField(SelectedGinning, verbose_name=_(
        "Selected Ginnings"), related_name="spinnings")
    vendor = models.ForeignKey(Vendor, verbose_name=_(
        "Vendor"), on_delete=models.CASCADE)

    timestamp = models.DateTimeField(_("Date"), default=timezone.now)

    @property
    def total_quantity(self):
        quantity = 0
        for selected_farmer in self.selected_ginnings.all():
            quantity += selected_farmer.quantity

        return quantity
    
    def __str__(self):
        return "-".join([selected_ginning.lot_no for selected_ginning in self.selected_ginnings.all()]) + f" ({self.total_quantity})"
    

class SpinningStatus(BaseModel):
    spinning = models.OneToOneField(Spinning, related_name="spinning_status", on_delete=models.PROTECT)

    UNDEFINED = 'Undefined'
    INBOUND = 'Inbound'
    IN_PROGRESS = 'In Progress'
    QC_PENDING = 'QC Pending'
    QC_APPROVED = 'QC Approved'
    QC_REJECTED = 'QC Rejected'
    COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (UNDEFINED, UNDEFINED),
        (INBOUND, INBOUND),
        (IN_PROGRESS, IN_PROGRESS),
        (QC_PENDING, QC_PENDING),
        (QC_APPROVED, QC_APPROVED),
        (QC_REJECTED, QC_REJECTED),
        (COMPLETED, COMPLETED),
    ]
    
    status = models.CharField(
        _("Status"), max_length=100, choices=STATUS_CHOICES, default=INBOUND)
    actual_count = models.CharField(_("Actual Count"), max_length=500, default="0")
    csp = models.CharField(_("CSP"), max_length=500, default="0")
    rkm = models.CharField(_("RKM"), max_length=500, default="0")
    ipi = models.CharField(_("IPI"), max_length=500, default="0")


class SpinningInProcess(BaseModel):
    spinning = models.OneToOneField(Spinning, verbose_name=_(
        "Spinning"), related_name='spinning_inprocess', on_delete=models.PROTECT)
    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now)
    name = models.CharField(_("Spinning Name"), max_length=500)
    raw_material_qty = models.FloatField(_("Raw material Quantity (Kgs)"), validators = [MinValueValidator(0.0)])
    output_yarn_qty = models.FloatField(_("Output Yarn Quantity (Kgs)"), validators = [MinValueValidator(0.0)])
    recovery = models.FloatField(_("Recovery %"), validators = [MinValueValidator(0.0), MaxValueValidator(100.0)])
    
    def save(self, *args, **kwargs):
        self.recovery = (self.output_yarn_qty / self.raw_material_qty) * 100
        super(SpinningInProcess, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.spinning} | {self.name}"


class SpinningOutbound(BaseModel):
    spinning = models.OneToOneField(Spinning, verbose_name=_(
        "Spinning"), related_name='spinning_outbound', on_delete=models.PROTECT)
    timestamp = models.DateTimeField(_("Date"))
    invoice_no = models.CharField(_("Invoice No."), max_length=500, default="0")
    product_name = models.CharField(_("Product Name"), max_length=500, default="0")
    lot_no = models.CharField(_("Lot No"), max_length=500, default="0")
    quantity = models.FloatField(_("Quantity (Kgs)"), validators = [MinValueValidator(0.0)])
    
    def __str__(self):
        return f"{self.spinning} | {self.quantity}"

