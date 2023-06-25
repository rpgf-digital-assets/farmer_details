import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


from users.models import User
from utils import BaseModel


# Create your models here.

class DefaultSelectOrPrefetchManager(models.Manager):
    """
    Default object for calling select related and prefetch related on models
    """

    def __init__(self, *args, **kwargs):
        self._select_related = kwargs.pop('select_related', None)
        self._prefetch_related = kwargs.pop('prefetch_related', None)

        super(DefaultSelectOrPrefetchManager, self).__init__(*args, **kwargs)


class Farmer(BaseModel):
    """Stores a single farmer information
    """
    
    class Meta:
        verbose_name_plural = _("Individuals")

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, primary_key=True)
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNDEFINED = 'UNDEFINED'
    GENDER_CHOICES = [
        (MALE, 'MALE'),
        (FEMALE, 'FEMALE'),
        (UNDEFINED, 'UNDEFINED'),
    ]
    gender = models.CharField(_("Gender"), max_length=30, default=UNDEFINED)
    birth_date = models.DateField(_("BirthDate"))
    age = models.IntegerField(_("Age"))
    aadhar_number = models.IntegerField(_("Aadhar Number"))
    registration_number = models.IntegerField(_("Farmer Tracnet Registration Number"))
    date_of_joining_of_program = models.DateField(_("Date of Joining of Program"))
    village = models.CharField(_("Village"), max_length=200)
    taluka = models.CharField(_("Taluka"), max_length=200)
    district = models.CharField(_("District"), max_length=200)
    state = models.CharField(_("State"), max_length=200)
    country = models.CharField(_("Country"), max_length=100)
    profile_image = models.ImageField(
        _("Profile Image"), upload_to="farmer_profile_image", default="farmer_profile_image/blank-profile-picture.png", blank=True, null=True)
    objects = DefaultSelectOrPrefetchManager(
        select_related=('user',),
    )
    
    def __str__(self):
        return f'{self.user}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class FarmerProject(BaseModel):
    """Store project information of a farmer
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ORGANIC = 'ORGANIC'
    SUSTAINABLE = 'SUSTAINABLE'
    UNDEFINED = 'UNDEFINED'
    TYPE_CHOICES = [
        (ORGANIC, 'ORGANIC'),
        (SUSTAINABLE, 'SUSTAINABLE'),
        (UNDEFINED, 'UNDEFINED'),
    ]
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default=UNDEFINED)
    ics_name = models.CharField(max_length=200)
    mandator_name = models.CharField(max_length=200)
    certification_agency_name = models.CharField(max_length=400)
    
    
class FarmerEducation(BaseModel):
    name = models.CharField(max_length=100)
    
class FarmerSocial(BaseModel):
    """Store social data of a farmer
    """
    education = models.ForeignKey(FarmerEducation, related_name='farmer_social')
    number_of_members_gt_18 = models.IntegerField(_("Number of members greater than 18"))
    number_of_members_lt_18 = models.IntegerField(_("Number of members less than 18"))
    total_family_members = models.IntegerField(_("Total family members"))
    number_of_members_attending_school = models.IntegerField(_("Number of members attending school"))
    HOUSING_CHOICES = [
        ('PUCCA', 'Puccs'),
        ('SEMI_PUCCA', 'Semi-Puccs'),
        ('KACHA', 'Kacha')
    ]
    housing = models.CharField(max_length=100, choices=HOUSING_CHOICES)
    electrification = models.BooleanField(_("Is there electricity?"))
    SOURCE_CHOICES = [
        ('BOREWELL', 'Borewell'),
        ('HANDPUMP', 'Handpump'),
        ('WELL', 'Well'),
        ('TAP', 'Tap'),
        ('RIVER', 'River'),
        ('OTHERS', 'others'),
    ]
    drinking_water_source = models.CharField(max_length=100, choices=SOURCE_CHOICES)
    distance_from_water_sources = models.IntegerField(_("Distance from water sources"))
    is_toilet_available = models.BooleanField(_("Is toilet available?"))
    COOKING_FUEL_CHOICES = [
        ('KEROSENE', 'Kerosene'),
        ('FIREWOOD', 'Firewood'),
        ('SOLAR_COOKER', 'Solar cooker'),
        ('LPG', 'LPG'),
    ]
    cooking_fuel = models.CharField(max_length=100, choices=COOKING_FUEL_CHOICES)
    life_or_health_insurance = models.BooleanField(_("Life or health insurance available?"))
    crop_insurance = models.BooleanField(_("Crop insurance available?"))
    crop_loan_taken = models.BooleanField(_("Crop loan taken from money lenders?"))
    agriculture_loan_taken = models.BooleanField(_("Agriculture loan taken from bank?"))
    MOBILE_TYPES = [
        ('NO', 'No'),
        ('FEATURE_PHONE', 'Feature Phone'),
        ('SMARTPHONE_WITHOUT_INTERNET', 'Smartphone without internet'),
        ('SMARTPHONE_WITH_INTERNET', 'Smartphone with internet'),
    ]
    mobile_phone_type = models.CharField(_("Mobile phone type"), max_length=100, choices=MOBILE_TYPES)
    bank_account_number = models.IntegerField(_("Bank account number"))
    bank_account_name = models.CharField(_("Bank account name"))
    bank_ifsc_code = models.CharField(_("Bank ifsc code"))
    
    
class FarmerLivestock(BaseModel):
    cow = models.IntegerField(_("Number of cow"))
    buffalo = models.IntegerField(_("Number of buffalo"))
    bullock = models.IntegerField(_("Number of bullock"))
    goat = models.IntegerField(_("Number of goat"))
    poultry = models.IntegerField(_("Number of poultry"))
    young_ones = models.IntegerField(_("Number of Heifer/Young ones"))
    total = models.IntegerField(_("Number of total livestock"))
 
 
class SoilTest(BaseModel):
    last_conducted = models.IntegerField(_("Last Soil test conducted in year"))
    soil_type = models.CharField(_("Soil type"))
    soil_texture = models.CharField(_("Soil texture"))
    soil_orgainc_matter = models.CharField(_("Soil orgainc matter"))
    soil_ph = models.CharField(_("Soil ph"))
    soil_drainage = models.CharField(_("Soil drainage"))
    soil_moisture = models.CharField(_("Soil Pressure"))
    

class FarmerLand(BaseModel):
    owned_land = models.IntegerField(_("Owned land in Hectare"))
    leased_land = models.IntegerField(_("Leased land in Hectare"))
    land_under_irrigation = models.IntegerField(_("Land under irrigation in Hectare"))
    IRRIGATION_CHOICES = [
        ('BOREWELL', 'Borewell'),
        ('OPEN_WELL', 'Open Well'),
        ('RIVER', 'River'),
        ('CANAL', 'Canal'),
        ('POND', 'Pond'),
        ('OTHERS', 'others'),
    ]
    main_source_of_irrigation = models.CharField(_("Main source of irrigation"), max_length=100, choices=IRRIGATION_CHOICES)
    IRRIGATION_TYPE_CHOICES = [
        ('OPEN_IRRIGATION', 'Open irrigation'),
        ('SPRINKLER_IRRIGATION', 'Sprinkler irrigation'),
        ('DRIP_IRRIGATION', 'Drip irrigation')
        ('OTHERS', 'Others'),
    ]
    type_of_irrigation = models.CharField(_("Type of irregation"), max_length=100, choices=IRRIGATION_TYPE_CHOICES)
    total_organic_land = models.IntegerField(_("Totalorganic Land in hectares"))
    number_of_plots_under_organic = models.IntegerField(_("Number of plots under organic management"), )
    PRODUCTION_SYSTEM_CHOICES = [
        ('PARALLEL', 'Parallel'),
        ('SPLIT', 'Split'),
        ('COMPLETE_ORGANIC', 'Complete Organic'),
    ]
    present_production_system = models.CharField(_("Current Production system"), max_length=100, choices=PRODUCTION_SYSTEM_CHOICES)
    organic_farming_start_year = models.IntegerField(_("Organ Farming Start Year"), )
    latitude = models.IntegerField(_("Latitude of land"))
    longitude = models.IntegerField(_("Longitude of land"))
    survey_number = models.IntegerField(_("Survey Number"))
    soil_test = models.ForeignKey(SoilTest, related_name="farm_land")
    
    @property
    def total_land(self):
        return self.owned_land + self.leased_land
    
    
class OrganicCropDetails(BaseModel):
    name = models.CharField(_("Name"), max_length=200)
    TYPE_CHOICES = [
        ("MAIN_CROP", 'Main crop'),
        ("INTER_CROP", 'Inter crop'),
        ("COVER_CROP", 'Cover crop'),
        ("MIXED_CROP", 'Mixed crop'),
    ]
    type = models.CharField(_("Type of soil"), max_length=200, choices=TYPE_CHOICES)
    area = models.IntegerField(_("Area of land in hectare"))
    date_of_sowing = models.DateField(_("Date of sowing of crop"))
    expected_date_of_harvesting = models.DateField(_("Expected date of harvest"))
    expected_yield = models.IntegerField(_("Expected yield in kg"))
    expected_productivity = models.IntegerField(_("Expected productivity in kg/ha"))
    
    
    