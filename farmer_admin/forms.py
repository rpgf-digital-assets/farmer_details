
import os 
from PIL import Image
from io import BytesIO
from django.conf import settings

from django.core.files.base import ContentFile

from django.forms import (
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
    FileField
)

from farmer.models import Farmer, FarmerEducation, FarmerLand, FarmerSocial
from users.models import User
from users.validators import validate_name, validate_phonenumber
from .utils import country_list

from django.db import transaction


class BaseCreationForm(ModelForm):
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.widget.input_type == 'checkbox':
                visible.field.widget.attrs['class'] = 'form-check-input'
            else:
                visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = f'Enter {visible.field.label}'
    


class FarmerCreationForm(BaseCreationForm):
    user = ModelChoiceField(required=False, queryset=User.objects.filter(
        is_active=True), empty_label="Select", disabled=True, widget=HiddenInput())
    
    first_name = CharField(label='First Name',validators=[validate_name], widget=TextInput(attrs={
        'placeholder': 'First Name'
    }))
    
    last_name = CharField(label='Last Name',validators=[validate_name], widget=TextInput(attrs={
        'class': 'form-control form-control-solid form-control-lg w-auto',
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
        widget=TextInput(attrs={'class': 'form-control form-control-lg form-control-solid w-auto',
        'placeholder': 'Business Phone',
    }))
    
    # country = CharField(label='Country', widget=Select(
    #     choices=country_list,
    #     attrs={
    #     'class': 'form-control form-select',
    #     'data-control': 'select2',
    #     'data-placeholder': 'select country'
    # }))
    
    
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
                    User.objects.get(phone=phone)
                    validation_errors.append(ValidationError(
                        'User already exists with the same phone number',
                        'user_already_exists'
                    ))
            except KeyError:
                User.objects.get(phone=phone)
                validation_errors.append(ValidationError(
                    'User already exists with the same phone number',
                    'user_already_exists'
                ))
        except User.DoesNotExist:
            # User does not exist we should create a new one
            pass
        
        if validation_errors: 
            raise ValidationError(validation_errors)
    
    
    
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
    class Meta:
        model = FarmerLand
        exclude = ['farmer']
    
    
    


    
    