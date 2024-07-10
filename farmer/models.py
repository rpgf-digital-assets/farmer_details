import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import date
from simple_history.models import HistoricalRecords

from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User
from users.validators import validate_positive_number
from utils.helpers import BaseModel


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
        User, verbose_name=_('User Name'), on_delete=models.PROTECT, primary_key=True)
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNDEFINED = 'UNDEFINED'
    GENDER_CHOICES = [
        (MALE, 'MALE'),
        (FEMALE, 'FEMALE'),
        (UNDEFINED, 'UNDEFINED'),
    ]
    gender = models.CharField(_("Gender"), max_length=30, choices=GENDER_CHOICES, default=UNDEFINED)
    birth_date = models.DateField(_("BirthDate"))
    aadhar_number = models.CharField(_("Aadhar Number"), max_length=20)
    registration_number = models.CharField(_("Farmer Tracenet Registration Number"), max_length=255)
    date_of_joining_of_program = models.DateField(_("Date of Joining of Program"))
    village = models.CharField(_("Village"), max_length=255)
    taluka = models.CharField(_("Taluka"), max_length=255)
    district = models.CharField(_("District"), max_length=255)
    state = models.CharField(_("State"), max_length=255)
    country = models.CharField(_("Country"), max_length=100, null=True, blank=True)
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
   

class OtherFarmer(BaseModel):
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)
    gender = models.CharField(_("Gender"), max_length=30, choices=Farmer.GENDER_CHOICES, default=Farmer.UNDEFINED)
    owned_land = models.PositiveIntegerField(_("Owned land in Hectare"), null=True, blank=True)
    identification_number = models.PositiveIntegerField(_("Identification Number"), null=True, blank=True)
    identification_file = models.FileField(_("Identification File"), upload_to="other_farmer/identification", null=True, blank=True)
    latitude = models.FloatField(_("Latitude of land"), null=True, blank=True)
    longitude = models.FloatField(_("Longitude of land"), null=True, blank=True)
    village = models.CharField(_("Village"), max_length=255)
    taluka = models.CharField(_("Taluka"), max_length=255)
    district = models.CharField(_("District"), max_length=255)
    state = models.CharField(_("State"), max_length=255)
    
    @property
    def user_display_name(self):
        return self.first_name + " " + self.last_name if self.last_name else self.first_name
    
    
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
    ics_name = models.CharField(max_length=255)
    mandator_name = models.CharField(max_length=255)
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
    number_of_members_gt_18 = models.PositiveIntegerField(_("Number of members greater than 18"))
    number_of_members_lt_18 = models.PositiveIntegerField(_("Number of members less than 18"))
    number_of_members_attending_school = models.PositiveIntegerField(_("Number of members attending school"))
    HOUSING_CHOICES = [
        ('Pukka', 'Pukka'),
        ('Semi pukka', 'Semi pukka'),
        ('Kucchha', 'Kucchha')
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
    distance_from_water_sources = models.PositiveIntegerField(_("Distance from water sources"))
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
    bank_account_number = models.PositiveIntegerField(_("Bank account number"), null=True, blank=True)
    bank_account_name = models.CharField(_("Bank account name"), max_length=100, null=True, blank=True)
    bank_ifsc_code = models.CharField(_("Bank ifsc code"), max_length=100, null=True, blank=True)

    @property
    def total_family_members(self):
        return self.number_of_members_gt_18 + self.number_of_members_lt_18
    
    
class FarmerLivestock(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='livestock', on_delete=models.PROTECT)
    cow = models.PositiveIntegerField(_("Number of cow"))
    buffalo = models.PositiveIntegerField(_("Number of buffalo"))
    bullock = models.PositiveIntegerField(_("Number of bullock"))
    goat = models.PositiveIntegerField(_("Number of goat"))
    poultry = models.PositiveIntegerField(_("Number of poultry"))
    young_ones = models.PositiveIntegerField(_("Number of Heifer/Young ones"))
    total = models.PositiveIntegerField(_("Number of total livestock"))
 

class FarmerLand(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='land', on_delete=models.PROTECT)
    owned_land = models.FloatField(_("Owned land in Hectare"))
    leased_land = models.FloatField(_("Leased land in Hectare"))
    land_under_irrigation = models.FloatField(_("Land under irrigation in Hectare"))
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
    total_organic_land = models.FloatField(_("Total organic Land in hectares"))
    number_of_plots_under_organic = models.PositiveIntegerField(_("Number of plots under organic management"), )
    PRODUCTION_SYSTEM_CHOICES = [
        ('PARALLEL', 'Parallel'),
        ('SPLIT', 'Split'),
        ('COMPLETE_ORGANIC', 'Complete Organic'),
    ]
    present_production_system = models.CharField(_("Current Production system"), max_length=100, choices=PRODUCTION_SYSTEM_CHOICES)
    organic_farming_start_year = models.PositiveIntegerField(_("Organ Farming Start Year"), )
    latitude = models.FloatField(_("Latitude of land"))
    longitude = models.FloatField(_("Longitude of land"))
    image = models.ImageField(verbose_name=_("Image of the land"), upload_to="farmer_land_images", null=True, blank=True)
    survey_number = models.CharField(_("Survey Number"), max_length=255)
    soil_test_conducted = models.BooleanField(_('Is soil testing done?'), )
    last_conducted = models.PositiveIntegerField(_("Last Soil test conducted in year"), null=True, blank=True)
    SOIL_TYPES = [
        ("Black", "Black"),
        ("Red", "Red"),
        ("Alluvial", "Alluvial"),
    ]
    soil_type = models.CharField(_("Soil type"), max_length=255, choices=SOIL_TYPES, null=True, blank=True)
    soil_texture = models.CharField(_("Soil texture"), max_length=255, null=True, blank=True)
    soil_organic_matter = models.CharField(_("Soil organic matter"), max_length=255, null=True, blank=True)
    soil_ph = models.CharField(_("Soil ph"), max_length=255, null=True, blank=True)
    soil_drainage = models.CharField(_("Soil drainage"), max_length=255, null=True, blank=True)
    soil_moisture = models.CharField(_("Soil Pressure"), max_length=255, null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        self.total_organic_land = self.owned_land + self.leased_land
        super(FarmerLand, self).save(*args, **kwargs)
    

class Season(BaseModel):
    name = models.CharField(_("Season Name"), max_length=255)
    start_date = models.DateField(_("Start Date"),) 
    end_date = models.DateField(_("End Date"),) 
    
    def __str__(self):
        return f"{self.name}"
    
class OrganicCropDetails(BaseModel):
    farmer = models.ForeignKey(Farmer, verbose_name=_("farmer"), related_name='organic_crop', on_delete=models.PROTECT)
    name = models.CharField(_("Name"), max_length=255)
    TYPE_CHOICES = [
        ("MAIN_CROP", 'Main crop'),
        ("INTER_CROP", 'Inter crop'),
        ("COVER_CROP", 'Cover crop'),
        ("MIXED_CROP", 'Mixed crop'),
    ]
    type = models.CharField(_("Type of crop"), max_length=100, choices=TYPE_CHOICES)
    area = models.FloatField(_("Area of land in hectare"))
    date_of_sowing = models.DateField(_("Date of sowing of crop"))
    expected_date_of_harvesting = models.DateField(_("Expected date of harvest"))
    expected_yield = models.FloatField(_("Expected yield in kg"))
    expected_productivity = models.FloatField(_("Expected Productivity"))
    season = models.ForeignKey(Season, verbose_name=_("Season"), related_name='organic_crop', on_delete=models.PROTECT)
    year = models.PositiveIntegerField(_("Season Year"), validators=[MaxValueValidator(9999)])
    
    def __str__(self):
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        self.expected_productivity = self.expected_yield
        if self.area > 0:
            self.expected_productivity = self.expected_yield / self.area
        
        super(OrganicCropDetails, self).save(*args, **kwargs)

    
class SeedDetails(BaseModel):
    organic_crop = models.ForeignKey(OrganicCropDetails, related_name='seed', on_delete=models.PROTECT)
    date_of_purchase = models.DateField(_("Date of purchase"))
    name_of_supplier = models.CharField(_("Name of supplier"), max_length=255)
    seed_for_sowing = models.FloatField(_("Amount of seed used for sowing (Kg)"))
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
    no_of_plants = models.FloatField(_("No of plants (Perennial crops)"))


class NutrientManagement(BaseModel):
    organic_crop = models.ForeignKey(OrganicCropDetails, related_name='nutrient', on_delete=models.PROTECT)
    FYM = 'FYM'
    COMPOST = 'COMPOST'
    VERMICOMPOST = 'VERMICOMPOST'
    OTHER = 'OTHER'
    TYPE_CHOICES = [
        (FYM, 'FYM'),
        (COMPOST, 'Compost'),
        (VERMICOMPOST, 'Vermicompost'),
        (OTHER, 'Other'),
    ]
    type = models.CharField(_("Type of fertiliser used"), max_length=100, choices=TYPE_CHOICES)
    custom_type = models.CharField(_("Other fertiliser used"), max_length=100, null=True, blank=True)
    
    ON_FARM = 'ON_FARM'
    OUTSOURCED = 'OUTSOURCED'
    SOURCE_CHOICES = [
        ('ON_FARM', 'on farm'),
        ('OUTSOURCED', 'outsourced'),
    ]
    source_of_fertilizer = models.CharField(_("Source of fertiliser"), max_length=100, choices=SOURCE_CHOICES)
    quantity_of_fertilizer = models.PositiveIntegerField(_("Qty of fertiliser applied (Kg)"))
    date_of_application = models.DateField(_("Date of application"))
    APPLICATION_CHOICES = [
        ('BROADCASTING', 'Broadcasting'),
        ('FERTIGATION', 'fertigation'),
        ('INCORPORATE', 'incorporate'),
        ('DRENCHING', 'drenching'),
    ]
    type_of_application = models.CharField(_("Type of application"), max_length=100, choices=APPLICATION_CHOICES)
    no_of_workdays_required = models.PositiveIntegerField(_("No of workdays required for activity"))
    
    # on farm inputs
    type_of_raw_material = models.CharField(_("Type of raw material used"), max_length=500, null=True, blank=True)
    quantity_used = models.PositiveIntegerField(_("Quantity used"), null=True, blank=True)
    starting_date = models.DateField(_("Starting date of preparation"), null=True, blank=True)
    date_of_manure = models.DateField(_("Date of manure ready"), null=True, blank=True)
    quantity_obtained = models.PositiveIntegerField(_("Qty obtained (Kg)"), null=True, blank=True)
    no_of_workdays_used = models.PositiveIntegerField(_("No of workdays used for activity"), null=True, blank=True)
    # Off Farm inputs
    sourcing_date = models.DateField(_("Date of sourcing"), null=True, blank=True)
    quantity_sourced = models.PositiveIntegerField(_("Qty sourced (Kg)"), null=True, blank=True)
    supplier_name = models.CharField(_("Name of supplier"), max_length=500, null=True, blank=True)
    

class PestDiseaseManagement(BaseModel):
    organic_crop = models.ForeignKey(OrganicCropDetails, related_name='pest_disease', on_delete=models.PROTECT)
    name_of_input = models.CharField(_("Name of input used"), max_length=255)
    quantity_of_input = models.PositiveIntegerField(_("Qty of input used (Kg or lit)"))
    source_of_input = models.CharField(_("Source of input"), max_length=100, choices=NutrientManagement.SOURCE_CHOICES)
    date_of_application = models.DateField(_("Date of application"))
    APPLICATION_CHOICES = [
        ('BRAODCASTING', 'Braodcasting'),
        ('SPRAYING', 'spraying'),
        ('FERTIGATION', 'fertigation'),
        ('DRENCHING', 'drenching'),
    ]
    type_of_application = models.CharField(_("Type of application"), max_length=100, choices=APPLICATION_CHOICES)
    targeted_pest_diseases = models.CharField(_("Targeted pest/disease"), max_length=255)
    
    # on farm inputs
    type_of_raw_material = models.CharField(_("Type of raw material used"), max_length=500, null=True, blank=True)
    quantity_used = models.PositiveIntegerField(_("No of workdays required for activity"), null=True, blank=True)
    starting_date = models.DateField(_("Starting date of preparation"), null=True, blank=True)
    date_of_manure = models.DateField(_("Date of manure ready"), null=True, blank=True)
    quantity_obtained = models.PositiveIntegerField(_("Qty obtained (Kg)"), null=True, blank=True)
    no_of_workdays_used = models.PositiveIntegerField(_("No of workdays used for activity"), null=True, blank=True)
    # Off Farm inputs
    sourcing_date = models.DateField(_("Date of sourcing"), null=True, blank=True)
    quantity_sourced = models.PositiveIntegerField(_("Qty sourced (Kg)"), null=True, blank=True)
    supplier_name = models.CharField(_("Name of supplier"), max_length=500, null=True, blank=True)
    
    
class WeedManagement(BaseModel):
    organic_crop = models.ForeignKey(OrganicCropDetails, related_name='weed', on_delete=models.PROTECT)
    activity_name = models.CharField(_("Name of activity carried out"), max_length=255)
    date_of_activity = models.DateField(_("Date of activity"))
    METHOD_CHOICES = [
        ('MANUAL', 'Manual'),
        ('ANIMAL', 'Animal'),
        ('MACHINERY', 'Machinery'),
    ]
    method = models.CharField(_("Method of activity"), max_length=100, choices=METHOD_CHOICES)
    workdays_utilized = models.PositiveIntegerField(_("No of workdays utilized for activity"))
    
    
class HarvestAndIncomeDetails(BaseModel): 
    organic_crop = models.ForeignKey(OrganicCropDetails, related_name='harvest_income', on_delete=models.PROTECT)
    SINGLE = 'SINGLE'
    MULTIPLE = 'MULTIPLE'
    TYPE_CHOICES = [
        (SINGLE, 'Single'),
        (MULTIPLE, 'Multiple'),
    ]
    type = models.CharField(verbose_name=_('Type of harvest (Single/multiple)'), max_length=100, choices=TYPE_CHOICES)
    first_harvest = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('First harvest'))
    first_harvest_date = models.DateField(verbose_name=_('First harvest date'))
    second_harvest = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Second harvest'), null=True, blank=True)
    second_harvest_date = models.DateField(verbose_name=_('Second harvest date'), null=True, blank=True)
    third_harvest = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name=_('Third harvest'), null=True, blank=True)
    third_harvest_date = models.DateField(verbose_name=_('Third harvest date'), null=True, blank=True)
    total_crop_harvested = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Total crop harvested'), null=True, blank=True)
    actual_crop_production = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Actual organic crop productivity (kg/ha)'))
    
    quantity_sold_fpo = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Quantity Sold through FPO (Kg)'))
    buyer_name = models.CharField(verbose_name=_('Name of Buyer'), max_length=500)
    price_paid_fpo = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Unit Sale Price paid by FPO Rs/kg'))
    premium_paid_fpo = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Premium paid by FPO(Rs/kg)'))
    total_price_received_fpo = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Total price received (Rs/Kg) including premium'))
    total_organic_sale_fpo = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Total income from sale of organic product through FPO'))
    
    quantity_sold_outside = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Quantity Sold Outside (Kg)'))
    outside_buyer_name = models.CharField(verbose_name=_('Name of Buyer outside'), max_length=500)
    price_paid_outside = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Unit Sale Price outside Rs/kg'))
    premium_paid_outside = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Premium paid outside (Rs/kg)'))
    total_price_received_outside = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Total price received (Rs/Kg) including premium'))
    total_organic_sale_outside = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Total income from sale of organic product outside'))
    
    gross_income = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Gross Income from sale of Organic crop (Rs) {sum of column U & P)'))
    payment_mode = models.CharField(verbose_name=_('Mode of payment'), max_length=500)
    payment_reference_number = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Payment Reference number '))
    unsold_quantity = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name=_('Quantity of organic harvest unsold/Balance (kg)'))
    
    def save(self, *args, **kwargs):
        if self.first_harvest and self.second_harvest and self.third_harvest:
            self.total_crop_harvested = self.first_harvest + self.second_harvest + self.third_harvest
        self.total_crop_harvested = self.first_harvest
        super(HarvestAndIncomeDetails, self).save(*args, **kwargs)
        
    # @property
    # def total_crop_harvested(self):
    #     if self.first_harvest and self.second_harvest and self.third_harvest:
    #         return self.first_harvest + self.second_harvest + self.third_harvest
    #     return self.first_harvest
    
    
class CostOfCultivation(BaseModel):
    organic_crop = models.ForeignKey(OrganicCropDetails, related_name='cost_of_cultivation', on_delete=models.PROTECT)
    # area = models.FloatField(verbose_name=_('Crop Area (Ha)'))
    input_source = models.CharField(verbose_name=_('Source of Input'), max_length=500, null=True, blank=True)
    manure_preparation_cost = models.PositiveIntegerField(verbose_name=_('Cost of Manure Preparation'))
    biofertilizer_preparation_cost = models.PositiveIntegerField(verbose_name=_('Cost of Biofertilizer Preparation'))
    biopesticide_preparation_cost = models.PositiveIntegerField(verbose_name=_('Cost of Bio pesticide Preparation'))
    seed_purchase_cost = models.PositiveIntegerField(verbose_name=_('Seed Purchase Costs'))
    irrigation_cost = models.PositiveIntegerField(verbose_name=_('Irrigation Costs'))
    machinery_cost = models.PositiveIntegerField(verbose_name=_('Machinery charges - owned & Hired'))
    input_cost = models.PositiveIntegerField(verbose_name=_('Input Costs '))
    animal_labour_cost = models.PositiveIntegerField(verbose_name=_('Animal labour cost - owned & hired'))
    land_preparation_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for land preparation'))
    sowing_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Sowing'))
    weed_management_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Weed management'))
    manure_application_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Manure Application'))
    biofertilizer_application_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Biofertilizer Application'))
    biopesticide_application_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Bio pesticide Application'))
    harvest_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Harvest'))
    total_labour_hiring_cost = models.PositiveIntegerField(verbose_name=_('Total Labour Hiring Costs'))
    other_cost = models.PositiveIntegerField(verbose_name=_('Other Costs (E.g Transport to Gin, Equipment Purchase etc.)'))
    total_cost = models.PositiveIntegerField(verbose_name=_('Total Cost'))
        
    
class ContaminationControl(BaseModel):
    organic_crop = models.ForeignKey(OrganicCropDetails, related_name='contamination_control', on_delete=models.PROTECT)
    CHANCES_CHOICES = [
        ('Seed', 'Seed'),
        ('machinery', 'machinery'),
        ('Water', 'Water'),
        ('Air', 'Air'),
        ('Neighbouring_field', 'Neighbouring field'),
        ('Drift_control_and_buffer_zone', 'Drift control & Buffer zone'),
        ('Storage', 'Storage'),
        ('Other', 'Other'),
    ]
    chances = models.CharField(verbose_name=_('Chances of contamination'), max_length=500, choices=CHANCES_CHOICES)
    details = models.CharField(verbose_name=_('Details of contamination'), max_length=500)
    preventive_measure_details = models.CharField(verbose_name=_('Details of Preventive measure taken'), max_length=500)
    control_measures_details = models.CharField(verbose_name=_('Details of control measures taken'), max_length=500)
    remark = models.CharField(verbose_name=_('Remark'), max_length=500)
    
    
class FarmerOrganicCropPdf(BaseModel):
    farmer = models.ForeignKey(Farmer, related_name='organic_crop_pdf', on_delete=models.PROTECT)
    pdf = models.FileField(upload_to='farmer/organic_crop_pdf', verbose_name=_("Organic Crop Pdf"))
    
    
class Costs(BaseModel):
    type = models.CharField(_("Type of fertilizer used"), max_length=100, choices=NutrientManagement.TYPE_CHOICES)
    manure_preparation_cost = models.PositiveIntegerField(verbose_name=_('Cost of Manure Preparation'))
    biofertilizer_preparation_cost = models.PositiveIntegerField(verbose_name=_('Cost of Biofertilizer Preparation'))
    biopesticide_preparation_cost = models.PositiveIntegerField(verbose_name=_('Cost of Bio pesticide Preparation'))
    seed_purchase_cost = models.PositiveIntegerField(verbose_name=_('Seed Purchase Costs'))
    irrigation_cost = models.PositiveIntegerField(verbose_name=_('Irrigation Costs'))
    land_preparation_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for land preparation'))
    sowing_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Sowing'))
    weed_management_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Weed management'))
    manure_application_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Manure Application'))
    biofertilizer_application_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Biofertilizer Application'))
    biopesticide_application_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Bio pesticide Application'))
    harvest_labour_cost = models.PositiveIntegerField(verbose_name=_('Labour Cost for Harvest'))
    
    
    