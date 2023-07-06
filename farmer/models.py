import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from farmer_details_app.models import BaseModel
from datetime import date
from simple_history.models import HistoricalRecords


from users.models import User


# Create your models here.

class DefaultSelectOrPrefetchManager(models.Manager):
    """
    Default object for calling select related and prefetch related on models
    """

    def __init__(self, *args, **kwargs):
        self._select_related = kwargs.pop('select_related', None)
        self._prefetch_related = kwargs.pop('prefetch_related', None)

        super(DefaultSelectOrPrefetchManager, self).__init__(*args, **kwargs)


class Farmer(models.Model):
    """Stores a single farmer information
    """
    
    class Meta:
        verbose_name_plural = _("Farmers")

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
    aadhar_number = models.IntegerField(_("Aadhar Number"))
    registration_number = models.IntegerField(_("Farmer Tracnet Registration Number"))
    date_of_joining_of_program = models.DateField(_("Date of Joining of Program"))
    village = models.CharField(_("Village"), max_length=200)
    taluka = models.CharField(_("Taluka"), max_length=200)
    district = models.CharField(_("District"), max_length=200)
    state = models.CharField(_("State"), max_length=200)
    country = models.CharField(_("Country"), max_length=100)
    profile_image = models.ImageField(
        _("Profile Image"), upload_to="farmer_profile_image", default="farmer_profile_image/blank-profile-picture.png")
    objects = DefaultSelectOrPrefetchManager(
        select_related=('user',),
    )
    history = HistoricalRecords()
    
    @property
    def age(self):
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
 
        return age
    
    def __str__(self):
        return f'{self.user}'

    

class FarmerProject(BaseModel):
    """Store project information of a farmer
    """
    farmer = models.ForeignKey(Farmer, related_name='project', on_delete=models.PROTECT)
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
    
    def __str__(self):
        return self.name
    
class FarmerSocial(BaseModel):
    """Store social data of a farmer
    """
    farmer = models.ForeignKey(Farmer, related_name='social', on_delete=models.PROTECT)
    education = models.ForeignKey(FarmerEducation, verbose_name=_("Education"), related_name='social', on_delete=models.PROTECT)
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
    bank_account_name = models.CharField(_("Bank account name"), max_length=100)
    bank_ifsc_code = models.CharField(_("Bank ifsc code"), max_length=100)
    
    
class FarmerLivestock(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='livestock', on_delete=models.PROTECT)
    cow = models.IntegerField(_("Number of cow"))
    buffalo = models.IntegerField(_("Number of buffalo"))
    bullock = models.IntegerField(_("Number of bullock"))
    goat = models.IntegerField(_("Number of goat"))
    poultry = models.IntegerField(_("Number of poultry"))
    young_ones = models.IntegerField(_("Number of Heifer/Young ones"))
    total = models.IntegerField(_("Number of total livestock"))
 
 

class FarmerLand(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='land', on_delete=models.PROTECT)
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
        ('DRIP_IRRIGATION', 'Drip irrigation'),
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
    latitude = models.FloatField(_("Latitude of land"))
    longitude = models.FloatField(_("Longitude of land"))
    image = models.ImageField(verbose_name=_("Image of the land"), upload_to="farmer_land_images")
    survey_number = models.IntegerField(_("Survey Number"))
    soil_test_conducted = models.BooleanField(_('Is soil testing done?'), )
    last_conducted = models.IntegerField(_("Last Soil test conducted in year"), null=True, blank=True)
    soil_type = models.CharField(_("Soil type"), max_length=200, null=True, blank=True)
    soil_texture = models.CharField(_("Soil texture"), max_length=200, null=True, blank=True)
    soil_organic_matter = models.CharField(_("Soil organic matter"), max_length=200, null=True, blank=True)
    soil_ph = models.CharField(_("Soil ph"), max_length=200, null=True, blank=True)
    soil_drainage = models.CharField(_("Soil drainage"), max_length=200, null=True, blank=True)
    soil_moisture = models.CharField(_("Soil Pressure"), max_length=200, null=True, blank=True)
    
    @property
    def total_land(self):
        return self.owned_land + self.leased_land
    
    
class OrganicCropDetails(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='organic_crop', on_delete=models.PROTECT)
    name = models.CharField(_("Name"), max_length=200)
    TYPE_CHOICES = [
        ("MAIN_CROP", 'Main crop'),
        ("INTER_CROP", 'Inter crop'),
        ("COVER_CROP", 'Cover crop'),
        ("MIXED_CROP", 'Mixed crop'),
    ]
    type = models.CharField(_("Type of crop"), max_length=100, choices=TYPE_CHOICES)
    area = models.IntegerField(_("Area of land in hectare"))
    date_of_sowing = models.DateField(_("Date of sowing of crop"))
    expected_date_of_harvesting = models.DateField(_("Expected date of harvest"))
    expected_yield = models.IntegerField(_("Expected yield in kg"))
    expected_productivity = models.IntegerField(_("Expected productivity in kg/ha"))
    
    
class SeedDetails(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='seed', on_delete=models.PROTECT)
    type = models.CharField(_("Type of crop"), max_length=100, choices=OrganicCropDetails.TYPE_CHOICES)
    date_of_purchase = models.DateField(_("Date of purchase"))
    name_of_supplier = models.CharField(_("Name of supplier"), max_length=200)
    seed_for_sowing = models.IntegerField(_("Amount of seed used for sowing (Kg)"))
    variety = models.CharField(_("Name of variety"), max_length=500)
    SEED_TYPES = [
        ('HYBRID', 'Hybrid'),
        ('VARIETY', 'Variety'),
        ('DESI', 'Desi'),
    ]
    seed_type = models.CharField(_("Seed Type"), max_length=100, choices=SEED_TYPES)
    SEED_SOURCES = [
        ('OWN', 'Own'),
        ('MARKET_SELF_BOUGHT', 'Market Self Bought'),
        ('MARKET_THROUGH_PROGRAMME', 'Market Through Programme'),
        ('FPC_FPO_FARMER_COLLECTIVE', 'FPC/FPO/farmer Collective'),
    ]
    source_of_seed = models.CharField(_("Main Source of Seed"), max_length=100, choices=SEED_SOURCES)
    treatment = models.CharField(_("Details of seed treatment"), max_length=500)
    no_of_plants = models.IntegerField(_("No of plants (Perennial crops)"))
    


class NutrientManagement(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='nutrient', on_delete=models.PROTECT)
    crop_name = models.CharField(_("Name of crop"), max_length=100)
    TYPE_CHOICES = [
        ('FYM', 'FYM'),
        ('COMPOST', 'Compost'),
        ('VERMICOMPOST', 'Vermicompost'),
    ]
    type = models.CharField(_("Type of fertiliser used"), max_length=100, choices=TYPE_CHOICES)
    SOURCE_CHOICES = [
        ('ON_FARM', 'on farm'),
        ('OUTSOURCED', 'outsourced'),
    ]
    souce_of_fertilizer = models.CharField(_("Source of fertiliser"), max_length=100, choices=SOURCE_CHOICES)
    quantity_of_fertilizer = models.IntegerField(_("Qty of fertiliser applied (Kg)"))
    date_of_application = models.DateField(_("Date of application"))
    APPLICATION_CHOICES = [
        ('BROADCASTING', 'Broadcasting'),
        ('FERTIGATION', 'fertigation'),
        ('INCORPORATE', 'incorporate'),
        ('DRENCHING', 'drenching'),
    ]
    type_of_application = models.CharField(_("Type of application"), max_length=100, choices=APPLICATION_CHOICES)
    no_of_workdays_required = models.IntegerField(_("No of workdays required for activity"))
    
    # on farm inputs
    type_of_raw_material = models.CharField(_("Type of raw material used"), max_length=500, null=True, blank=True)
    quantity_used = models.IntegerField(_("No of workdays required for activity"), null=True, blank=True)
    starting_date = models.DateField(_("Starting date of preparation"), null=True, blank=True)
    date_of_manure = models.DateField(_("Date of manure ready"), null=True, blank=True)
    quantity_obtained = models.IntegerField(_("Qty obtained (Kg)"), null=True, blank=True)
    no_of_workdays_used = models.IntegerField(_("No of workdays used for activity"), null=True, blank=True)
    # Off Farm inputs
    sourcing_date = models.DateField(_("Date of sourcing"), null=True, blank=True)
    quantity_sourced = models.IntegerField(_("Qty sourced (Kg)"), null=True, blank=True)
    supplier_name = models.CharField(_("Name of supplier"), max_length=500, null=True, blank=True)
    
    

class PestDiseaseManagement(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='pest_disease', on_delete=models.PROTECT)
    crop_name = models.CharField(_("Name of crop"), max_length=100)
    name_of_input = models.CharField(_("Name of input used"), max_length=200)
    quantity_of_input = models.IntegerField(_("Qty of input used (Kg or lit)"))
    souce_of_input = models.CharField(_("Source of input"), max_length=100, choices=NutrientManagement.SOURCE_CHOICES)
    date_of_application = models.DateField(_("Date of application"))
    APPLICATION_CHOICES = [
        ('BRAODCASTING', 'Braodcasting'),
        ('SPRAYING', 'spraying'),
        ('FERTIGATION', 'fertigation'),
        ('DRENCHING', 'drenching'),
    ]
    type_of_application = models.CharField(_("Type of application"), max_length=100, choices=APPLICATION_CHOICES)
    targeted_pest_diseases = models.CharField(_("Targeted pest/disease"), max_length=200)
    
    # on farm inputs
    type_of_raw_material = models.CharField(_("Type of raw material used"), max_length=500, null=True, blank=True)
    quantity_used = models.IntegerField(_("No of workdays required for activity"), null=True, blank=True)
    starting_date = models.DateField(_("Starting date of preparation"), null=True, blank=True)
    date_of_manure = models.DateField(_("Date of manure ready"), null=True, blank=True)
    quantity_obtained = models.IntegerField(_("Qty obtained (Kg)"), null=True, blank=True)
    no_of_workdays_used = models.IntegerField(_("No of workdays used for activity"), null=True, blank=True)
    # Off Farm inputs
    sourcing_date = models.DateField(_("Date of sourcing"), null=True, blank=True)
    quantity_sourced = models.IntegerField(_("Qty sourced (Kg)"), null=True, blank=True)
    supplier_name = models.CharField(_("Name of supplier"), max_length=500, null=True, blank=True)
    
    
    
    
class WeedManagement(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='weed', on_delete=models.PROTECT)
    activity_name = models.CharField(_("Name of activity carried out"), max_length=200)
    date_of_activity = models.DateField(_("Date of activity"))
    METHOD_CHOICES = [
        ('MANUAL', 'Manual'),
        ('ANIMAL', 'Animal'),
        ('MACHINERY', 'Machinery'),
    ]
    method = models.CharField(_("Method of activity"), max_length=100, choices=METHOD_CHOICES)
    workdays_utilized = models.IntegerField(_("No of workdays utilised for activity"))
    
    
    
    
    
    
    