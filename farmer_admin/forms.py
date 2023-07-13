from django.forms import (
    BaseFormSet,
    CharField,
    EmailField,
    EmailInput,
    FileInput,
    HiddenInput,
    ImageField,
    Form,
    ModelChoiceField,
    ModelForm,
    Select,
    TextInput,
    ValidationError,
    ChoiceField,
    BooleanField,
    CheckboxInput,
    DateInput,
    DateField,
    DateTimeField,
    IntegerField,
    NumberInput,
    Textarea,
    FileField,
    formset_factory
)

from farmer.models import ContaminationControl, CostOfCultivation, Farmer, FarmerEducation, FarmerLand, FarmerSocial, HarvestAndIncomeDetails, NutrientManagement, OrganicCropDetails, OtherFarmer, PestDiseaseManagement, Season, SeedDetails, WeedManagement
from farmer_details_app.models import SelectedGinningFarmer, Vendor
from users.models import User
from users.validators import validate_name, validate_phonenumber

from django.db import transaction

class BaseSelectedFarmerFormSet(BaseFormSet):
    def clean(self):
        """Checks that no two selected ginning farmer are same."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        selected_farmer_list = []
        for form in self.forms:
            
            if self.can_delete and self._should_delete_form(form):
                continue
            farmer = form.cleaned_data.get("farmer")
            farmer_name = form.cleaned_data.get("farmer_name")
            quantity = form.cleaned_data.get("quantity")
            if (farmer, farmer_name, quantity) in selected_farmer_list:
                raise ValidationError("Selected farmers in a set must be distinct.")
            selected_farmer_list.append((farmer, farmer_name, quantity))
            if not farmer and not farmer_name and not quantity:
                raise ValidationError("Cannot submit an empty form")
        
        
class BaseContaminationFormSet(BaseFormSet):
    def clean(self):
        """Checks that no two selected ginning farmer are same."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        chances_list = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            chances = form.cleaned_data.get("chances")
            details = form.cleaned_data.get("details")
            preventive_measure_details = form.cleaned_data.get("preventive_measure_details")
            control_measures_details = form.cleaned_data.get("control_measures_details")
            remark = form.cleaned_data.get("remark")
            if chances in chances_list:
                raise ValidationError("Selected Chances must be distinct.")
            chances_list.append(chances)
            if not chances and not details and not preventive_measure_details and not control_measures_details and not remark:
                raise ValidationError("Cannot submit an empty form")
        

class BaseCreationForm(ModelForm):
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            print("🐍 File: farmer_admin/forms.py | Line: 52 | __init__ ~ visible.field.widget.input_type",visible.field.widget.input_type)
            if visible.field.widget.input_type == 'checkbox':
                try:
                    visible.field.widget.attrs['class'] = f'{visible.field.widget.attrs["class"]} form-check-input'
                except KeyError:
                    visible.field.widget.attrs['class'] = 'form-check-input'
            else:
                try:
                    visible.field.widget.attrs['class'] = f'{visible.field.widget.attrs["class"]} form-control'
                except KeyError:
                    visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = f'Enter {visible.field.label}'
    

class FarmerCreationForm(BaseCreationForm):
    user = ModelChoiceField(required=False, queryset=User.objects.filter(
        is_active=True), empty_label="Select", disabled=True, widget=HiddenInput())
    
    first_name = CharField(label='First Name',validators=[validate_name], widget=TextInput(attrs={
        'placeholder': 'First Name'
    }))
    
    last_name = CharField(label='Last Name',validators=[validate_name], widget=TextInput(attrs={
        'placeholder': 'Last Name'
    }))

    birth_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'form-control datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    date_of_joining_of_program = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    gender = ChoiceField(choices = Farmer.GENDER_CHOICES, required=True,
        widget=Select(attrs={
        'class': 'form-control form-select'
    }))
    phone = CharField(label='Business Phone', validators=[validate_phonenumber],
        widget=TextInput(attrs={
        'placeholder': 'Business Phone',
    }))
    
    
    class Meta:
        model = Farmer
        exclude = ['country']

    field_order = ['first_name', 'last_name', 'gender', 'birth_date', 'aadhar_number', 'phone', 'registration_number', 'date_of_joining_of_program',
                   'village', 'taluka', 'district', 'state', 'profile_image']
    
    def clean(self):
        cleaned_data = super().clean()
        validation_errors = []
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        gender = cleaned_data.get('gender')
        birth_date = cleaned_data.get('birth_date')
        aadhar_number = cleaned_data.get('aadhar_number')
        phone = cleaned_data.get('phone')
        registration_number = cleaned_data.get('registration_number')
        date_of_joining_of_program = cleaned_data.get('date_of_joining_of_program')
        village = cleaned_data.get('village')
        taluka = cleaned_data.get('taluka')
        district = cleaned_data.get('district')
        state = cleaned_data.get('state')
        
        # Check if the user already exists with the same name and phone number
        try: 
            # Check if user phone numer changed
            try:
                if self.initial['phone'] != phone:
                    user = User.objects.get(is_active=True, phone=f'{phone}')
                    print("🐍 File: farmer_admin/forms.py | Line: 130 | clean ~ user",user, phone)
                    validation_errors.append(ValidationError(
                        'User already exists with the same phone number',
                        'user_already_exists'
                    ))
            except KeyError:
                User.objects.get(is_active=True, phone=phone)
                validation_errors.append(ValidationError(
                    'User already exists with the same phone number',
                    'user_already_exists'
                ))
        except User.DoesNotExist:
            # User does not exist we should create a new one
            pass
        
        if validation_errors: 
            raise ValidationError(validation_errors)
    
    
class OtherFarmerCreationForm(BaseCreationForm):
    class Meta:
        model = OtherFarmer
        fields = '__all__'

    
class FarmerSocialCreationFrom(BaseCreationForm):
    class Meta:
        model = FarmerSocial
        exclude = ['farmer']
        
    field_order = ['education', 'number_of_members_gt_18', 'number_of_members_lt_18', 'total_family_members', 
                   'number_of_members_attending_school', 'housing', 'drinking_water_source',
                   'distance_from_water_sources', 'electrification', 'is_toilet_available', 'life_or_health_insurance', 'crop_insurance',
                   'crop_loan_taken', 'agriculture_loan_taken', 'cooking_fuel', 'mobile_phone_type', 
                   'bank_account_number', 'bank_account_name', 'bank_ifsc_code']

    education = ModelChoiceField(queryset=FarmerEducation.objects.all(), empty_label="Select", 
        widget=Select(attrs={
        'class': 'form-control form-select'
    }))
    
    
class FarmerLandDetailsCreationFrom(BaseCreationForm):
    last_conducted = CharField(required=False, widget=TextInput(attrs={
        'class': 'soil-testing-inputs'
    }))
    soil_type = CharField(required=False, widget=TextInput(attrs={
        'class': 'soil-testing-inputs'
    }))
    soil_texture = CharField(required=False, widget=TextInput(attrs={
        'class': 'soil-testing-inputs'
    }))
    soil_organic_matter = CharField(required=False, widget=TextInput(attrs={
        'class': 'soil-testing-inputs'
    }))
    soil_ph = CharField(required=False, widget=TextInput(attrs={
        'class': 'soil-testing-inputs'
    }))
    soil_drainage = CharField(required=False, widget=TextInput(attrs={
        'class': 'soil-testing-inputs'
    }))
    soil_moisture = CharField(required=False, widget=TextInput(attrs={
        'class': 'soil-testing-inputs'
    }))
    
    class Meta:
        model = FarmerLand
        exclude = ['farmer']
        
    def clean(self):
        cleaned_data = super().clean()
        validation_errors = []
        
        soil_test_conducted = cleaned_data.get('soil_test_conducted')
        last_conducted = cleaned_data.get('last_conducted')
        soil_type = cleaned_data.get('soil_type')
        soil_texture = cleaned_data.get('soil_texture')
        soil_organic_matter = cleaned_data.get('soil_organic_matter')
        soil_ph = cleaned_data.get('soil_ph')
        soil_drainage = cleaned_data.get('soil_drainage')
        soil_moisture = cleaned_data.get('soil_moisture')
        
        if soil_test_conducted == True:
            if ('' in [last_conducted, soil_type, soil_texture, soil_organic_matter, soil_ph, soil_drainage, soil_moisture]):
                validation_errors.append(ValidationError('Soil testing inputs are required if soil test is conducted.', 'soil_test_required'))
        
        if validation_errors: 
            raise ValidationError(validation_errors)
        
        
class FarmerOrganicCropDetailForm(BaseCreationForm):
    date_of_sowing = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'form-control datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    expected_date_of_harvesting = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'form-control datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    
    class Meta:
        model = OrganicCropDetails
        exclude = ['farmer']
        
        
class FarmerSeedDetailsForm(BaseCreationForm):
    date_of_purchase = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'form-control datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    
    class Meta:
        model = SeedDetails
        exclude = ['organic_crop']
        
        
class FarmerNutritionManagementForm(BaseCreationForm):
    source_field_name = 'souce_of_fertilizer'
    
    type_of_raw_material = CharField(required=False, widget=TextInput(attrs={
        'class': 'on-farm-input'
    }))
    quantity_used = IntegerField(required=False, widget=NumberInput(attrs={
        'class': 'on-farm-input',
    }))
    starting_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'on-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    date_of_manure = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'on-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    quantity_obtained = IntegerField(required=False, widget=NumberInput(attrs={
        'class': 'on-farm-input',
    }))
    no_of_workdays_used = IntegerField(required=False, widget=NumberInput(attrs={
        'class': 'on-farm-input',
    }))
    # Off Farm inputs
    sourcing_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    quantity_sourced = IntegerField(required=False, widget=NumberInput(attrs={
        'class': 'off-farm-input',
    }))
    supplier_name = CharField(required=False, widget=TextInput(attrs={
        'class': 'off-farm-input'
    }))
    class Meta:
        model = NutrientManagement
        exclude = ['organic_crop',]
    
    def clean(self):
        cleaned_data = super().clean()
        validation_errors = []
        
        source_field_name = cleaned_data.get(self.source_field_name)
        
        type_of_raw_material = cleaned_data.get('type_of_raw_material')
        quantity_used = cleaned_data.get('quantity_used')
        starting_date = cleaned_data.get('starting_date')
        date_of_manure = cleaned_data.get('date_of_manure')
        quantity_obtained = cleaned_data.get('quantity_obtained')
        no_of_workdays_used = cleaned_data.get('no_of_workdays_used')
        sourcing_date = cleaned_data.get('sourcing_date')
        quantity_sourced = cleaned_data.get('quantity_sourced')
        supplier_name = cleaned_data.get('supplier_name')
        
        if source_field_name == NutrientManagement.ON_FARM:
            if ('' in [type_of_raw_material, quantity_used, starting_date, date_of_manure, quantity_obtained, no_of_workdays_used]):
                validation_errors.append(ValidationError('ON farm inputs are required if souce is ON farm.', 'on_farm_required'))
        elif source_field_name == NutrientManagement.OUTSOURCED:
            if ('' in [sourcing_date, quantity_sourced, supplier_name]):
                validation_errors.append(ValidationError('OFF farm inputs are required if souce is OFF farm.', 'off_farm_required'))

        
        if validation_errors: 
            raise ValidationError(validation_errors)
    
    
    
class FarmerPestDiseaseManagementForm(FarmerNutritionManagementForm):
    source_field_name = 'souce_of_input'
    
    class Meta: 
        model = PestDiseaseManagement
        exclude = ['organic_crop']
    
    
class WeedManagementForm(BaseCreationForm):
    date_of_activity = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    class Meta:
        model = WeedManagement
        exclude = ['organic_crop']


class HarvestAndIncomeDetailForm(BaseCreationForm):
    first_harvest_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    second_harvest_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
            'class': 'off-farm-input datetimepicker-input w-auto',
            'placeholder': 'Enter date in YYYY-MM-DD',
            'data-target': '#kt_datetimepicker_3'
        }))
    third_harvest_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    class Meta:
        model = HarvestAndIncomeDetails
        exclude = ['organic_crop']



class CostOfCultivationForm(BaseCreationForm):
    class Meta:
        model = CostOfCultivation
        exclude = ['organic_crop']

    

class ContaminationControlForm(BaseCreationForm):
    class Meta:
        model = ContaminationControl
        exclude = ['organic_crop']
    

ContaminationControlFormSet = formset_factory(ContaminationControlForm, formset=BaseContaminationFormSet, extra=1, min_num=1)
    
class VendorCreateForm(BaseCreationForm):
    class Meta:
        model = Vendor
        exclude = ['id']



class SelectedGinningFarmerForm(ModelForm): 
    farmer = ModelChoiceField(required=False, queryset=Farmer.objects.all(), widget=Select(
        attrs={
            'class': 'form-control'
        }
    ))
    farmer_name = CharField(required=False, widget=TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    quantity = IntegerField(widget=NumberInput(attrs={
        'class': 'form-control'
    }))
    
    class Meta:
        model = SelectedGinningFarmer
        exclude = ['id']
        
    def clean(self):
        cleaned_data = super().clean()
        validation_errors = []

        farmer = cleaned_data.get('farmer')
        farmer_name = cleaned_data.get('farmer_name')
        
        if not farmer and not farmer_name:
            validation_errors.append(ValidationError('Select a farmer or type the farmer name', 'farmer_required'))
        if farmer and farmer_name:
            validation_errors.append(ValidationError('Select either farmer or type the farmer name', 'farmer_required'))
        
        if validation_errors: 
            raise ValidationError(validation_errors)
        
        

        
SelectedGinningFarmerFormSet = formset_factory(SelectedGinningFarmerForm, extra=1, formset=BaseSelectedFarmerFormSet, min_num=1)


class GinningMappingForm(Form):

    vendor = ModelChoiceField(required=True, queryset=Vendor.objects.all(), widget=Select(
        attrs={
            'class': 'form-control'
        }
    ))

    
    
class SeasonCreateForm(BaseCreationForm):
    class Meta:
        model = Season
        fields = '__all__'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    