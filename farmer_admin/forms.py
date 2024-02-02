from datetime import datetime
from typing import Any, Dict

from django.forms import (
    BaseFormSet,
    CharField,
    DateTimeInput,
    EmailField,
    EmailInput,
    FileInput,
    FloatField,
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
from django.db.models import Sum, F, Q, ExpressionWrapper, FloatField as _FloatField
from django.db.models.functions import Coalesce

from farmer.models import ContaminationControl, CostOfCultivation, Costs, Farmer, FarmerEducation, FarmerLand, FarmerSocial, HarvestAndIncomeDetails, NutrientManagement, OrganicCropDetails, OtherFarmer, PestDiseaseManagement, Season, SeedDetails, WeedManagement
from farmer_details_app.models import ApplicationConfiguration, BulkUpload, Ginning, GinningInProcess, GinningOutbound, GinningStatus, SelectedGinning, SelectedGinningFarmer, Spinning, SpinningInProcess, SpinningOutbound, SpinningStatus, Vendor
from users.models import User
from users.validators import validate_name, validate_phonenumber, validate_positive_number


class PositiveIntegerField(IntegerField):
    default_validators = [validate_positive_number]


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
            preventive_measure_details = form.cleaned_data.get(
                "preventive_measure_details")
            control_measures_details = form.cleaned_data.get(
                "control_measures_details")
            remark = form.cleaned_data.get("remark")
            if chances in chances_list:
                raise ValidationError("Selected Chances must be distinct.")
            chances_list.append(chances)
            if not chances and not details and not preventive_measure_details and not control_measures_details and not remark:
                raise ValidationError("Cannot submit an empty form")


class BaseFarmerOrganicCropFormSet(BaseFormSet):
    def clean(self):
        """Checks that no two selected ginning farmer are same."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            if not form.cleaned_data:
                raise ValidationError("Cannot submit an empty form")


class BaseCreationForm(ModelForm):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.kwargs = kwargs.pop('kwargs', None)
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            # print("🐍 File: farmer_admin/forms.py | Line: 52 | __init__ ~ visible.field.widget.input_type",visible.field.widget.input_type)
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

    first_name = CharField(label='First Name', validators=[validate_name], widget=TextInput(attrs={
        'placeholder': 'First Name'
    }))

    last_name = CharField(label='Last Name', validators=[validate_name], widget=TextInput(attrs={
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
    gender = ChoiceField(choices=Farmer.GENDER_CHOICES, required=True,
                         widget=Select(attrs={
                             'class': 'form-control form-select'
                         }))
    phone = CharField(label='Phone Number', validators=[validate_phonenumber],
                      widget=TextInput(attrs={
                            'placeholder': 'Phone Number',
                            'autocomplete': "off",
                            "data-intl-tel-input-id": "0"
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
        date_of_joining_of_program = cleaned_data.get(
            'date_of_joining_of_program')
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
    identification_file = FileField(required=False, widget=FileInput())

    class Meta:
        model = OtherFarmer
        fields = '__all__'


class FarmerSocialCreationFrom(BaseCreationForm):
    class Meta:
        model = FarmerSocial
        exclude = ['farmer']

    field_order = ['education', 'number_of_members_gt_18', 'number_of_members_lt_18',
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
        exclude = ['farmer', 'total_organic_land']

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
                validation_errors.append(ValidationError(
                    'Soil testing inputs are required if soil test is conducted.', 'soil_test_required'))

        if validation_errors:
            raise ValidationError(validation_errors)


######################### Organic Crop Forms::BEGIN ################################


class FarmerOrganicCropDetailForm(BaseCreationForm):

    def get_year_choices():
        year_choices = []
        current_date = datetime.now()
        for i in range(-2, 5):
            year_choices.append((current_date.year + i, current_date.year + i))
        return year_choices

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

    year = ChoiceField(choices=get_year_choices(), widget=Select(
        attrs={
            'class': 'form-control'
        }
    ))

    season = ModelChoiceField(queryset=Season.objects.filter(is_active=True))

    class Meta:
        model = OrganicCropDetails
        exclude = ['farmer', 'expected_productivity']


class FarmerSeedDetailsForm(BaseCreationForm):
    date_of_purchase = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'form-control datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))

    class Meta:
        model = SeedDetails
        exclude = ['organic_crop']


FarmerSeedDetailsFormSet = formset_factory(
    FarmerSeedDetailsForm, formset=BaseFarmerOrganicCropFormSet, extra=0, min_num=1)


class FarmerNutritionManagementForm(BaseCreationForm):
    source_field_name = 'souce_of_fertilizer'

    type_of_raw_material = CharField(required=False, widget=TextInput(attrs={
        'class': 'on-farm-input'
    }))
    quantity_used = PositiveIntegerField(required=False, widget=NumberInput(attrs={
        'class': 'on-farm-input',
    }))

    date_of_application = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))

    starting_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'on-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    date_of_manure = DateField(initial='', input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'on-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    quantity_obtained = PositiveIntegerField(required=False, widget=NumberInput(attrs={
        'class': 'on-farm-input',
    }))
    no_of_workdays_used = PositiveIntegerField(required=False, widget=NumberInput(attrs={
        'class': 'on-farm-input',
    }))
    # Off Farm inputs
    sourcing_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    quantity_sourced = PositiveIntegerField(required=False, widget=NumberInput(attrs={
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
                validation_errors.append(ValidationError(
                    'ON farm inputs are required if souce is ON farm.', 'on_farm_required'))
        elif source_field_name == NutrientManagement.OUTSOURCED:
            if ('' in [sourcing_date, quantity_sourced, supplier_name]):
                validation_errors.append(ValidationError(
                    'OFF farm inputs are required if souce is OFF farm.', 'off_farm_required'))

        if validation_errors:
            raise ValidationError(validation_errors)


FarmerNutritionManagementFormSet = formset_factory(
    FarmerNutritionManagementForm, formset=BaseFarmerOrganicCropFormSet, extra=0, min_num=1)


class FarmerPestDiseaseManagementForm(FarmerNutritionManagementForm):
    source_field_name = 'souce_of_input'

    date_of_application = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))

    class Meta:
        model = PestDiseaseManagement
        exclude = ['organic_crop']


FarmerPestDiseaseManagementFormSet = formset_factory(
    FarmerPestDiseaseManagementForm, formset=BaseFarmerOrganicCropFormSet, extra=0, min_num=1)


class WeedManagementForm(BaseCreationForm):
    date_of_activity = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))

    class Meta:
        model = WeedManagement
        exclude = ['organic_crop']


WeedManagementFormSet = formset_factory(
    WeedManagementForm, formset=BaseFarmerOrganicCropFormSet, extra=0, min_num=1)


class HarvestAndIncomeDetailForm(BaseCreationForm):
    first_harvest_date = DateField(input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    second_harvest_date = DateField(required=False, input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))
    third_harvest_date = DateField(required=False, input_formats=['%Y-%m-%d'], widget=DateInput(attrs={
        'class': 'off-farm-input datetimepicker-input w-auto',
        'placeholder': 'Enter date in YYYY-MM-DD',
        'data-target': '#kt_datetimepicker_3'
    }))

    class Meta:
        model = HarvestAndIncomeDetails
        exclude = ['organic_crop']

    def clean(self):
        validation_errors = []
        cleaned_data = super().clean()
        type = cleaned_data.get('type')
        total_crop_harvested = cleaned_data.get('total_crop_harvested')
        quantity_sold_fpo = cleaned_data.get('quantity_sold_fpo')
        quantity_sold_outside = cleaned_data.get('quantity_sold_outside')
        unsold_quantity = cleaned_data.get('unsold_quantity')
        if type == HarvestAndIncomeDetails.MULTIPLE:
            if not cleaned_data.get('second_harvest', None) and not cleaned_data.get('third_harvest', None):
                self.add_error('second_harvest', ValidationError(
                    "Second harvest is required if type is multiple"))
                
        if total_crop_harvested != (quantity_sold_fpo + quantity_sold_outside + unsold_quantity):
            validation_errors.append(ValidationError(
                    "Total crop harvested should be sum of all the quantities."))

        if validation_errors:
            raise ValidationError(validation_errors)

HarvestAndIncomeDetailFormSet = formset_factory(
    HarvestAndIncomeDetailForm, formset=BaseFarmerOrganicCropFormSet, extra=0, min_num=1)


class CostOfCultivationForm(BaseCreationForm):
    class Meta:
        model = CostOfCultivation
        exclude = ['organic_crop']


CostOfCultivationFormSet = formset_factory(
    CostOfCultivationForm, formset=BaseFarmerOrganicCropFormSet, extra=0, min_num=1)


class ContaminationControlForm(BaseCreationForm):
    class Meta:
        model = ContaminationControl
        exclude = ['organic_crop']

    def clean(self):
        chances = self.cleaned_data.get('chances', None)
        # if self.instance.pk:
        # Its an update request
        # Check if the chances field has changed
        # if 'chances' in self.changed_data:
        #     # Chances changed check if it already exists
        #     if ContaminationControl.objects.filter(organic_crop=self.instance.organic_crop, chances=chances).exists():
        #         self.add_error('chances', ValidationError('Chances already exists'))
        # For Create request add condition in view


ContaminationControlFormSet = formset_factory(
    ContaminationControlForm, formset=BaseContaminationFormSet, extra=0, min_num=1)


######################### Organic Crop Forms::END ################################


######################### Ginning Forms::BEGIN ################################
class CustomFarmerModelChoiceField(ModelChoiceField):

    def label_from_instance(self, obj):
        if obj.organic_crop:
            cotton_crop = obj.organic_crop.filter(name__iexact="cotton").first()
            if cotton_crop:
                if cotton_crop.harvest_income.all():
                    total_quantity = cotton_crop.harvest_income.aggregate(total_quantity=Sum('quantity_sold_fpo') - Sum('quantity_sold_outside'))['total_quantity']
                    total_ginned = Ginning.objects.filter(selected_farmers__farmer__in=[obj]).exclude(ginning_status__status__in=[GinningStatus.QC_REJECTED])\
                                    .aggregate(total_ginned=Coalesce(Sum('selected_farmers__quantity'), 0.0))['total_ginned']
                    return f'{obj.user} ({total_quantity - total_ginned} Kg)'
        return f'{obj.user}'

class SelectFarmerForm(ModelForm):
    farmer = CustomFarmerModelChoiceField(required=False, queryset=Farmer.objects.filter(organic_crop__name__iexact="cotton"), widget=Select(
        attrs={
            'class': 'form-control'
        }
    ))
    farmer_name = CharField(required=False, widget=TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    quantity = PositiveIntegerField(widget=NumberInput(attrs={
        'class': 'form-control'
    }))
    
    price = PositiveIntegerField(widget=NumberInput(attrs={
        'class': 'form-control'
    }))
    
    slip_no = CharField(required=True, widget=TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    inward_lot_no = CharField(required=True, widget=TextInput(
        attrs={
            'class': 'form-control'
        }
    ))

    class Meta:
        model = SelectedGinningFarmer
        exclude = ['id']

    def clean(self):
        cleaned_data = super().clean()
        validation_errors = []

        farmer = cleaned_data.get('farmer')
        farmer_name = cleaned_data.get('farmer_name')

        if not farmer and not farmer_name:
            validation_errors.append(ValidationError(
                'Select a farmer or type the farmer name', 'farmer_required'))
        if farmer and farmer_name:
            validation_errors.append(ValidationError(
                'Select either farmer or type the farmer name', 'farmer_required'))

        if validation_errors:
            raise ValidationError(validation_errors)


class SelectFarmerFormSet(BaseFormSet):
    def clean(self):
        """Checks that no two selected ginning farmer are same."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        distinct_farmer_quantity_mapping = {}
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            farmer = form.cleaned_data.get("farmer")
            quantity = form.cleaned_data.get("quantity")
            if farmer:
                try:
                    distinct_farmer_quantity_mapping[str(farmer.pk)] += quantity
                except KeyError:
                    distinct_farmer_quantity_mapping[str(farmer.pk)] = quantity
        validation_errors = []
        for farmer_pk in distinct_farmer_quantity_mapping.keys():
            farmer = Farmer.objects.get(pk=farmer_pk)
            organic_crop = OrganicCropDetails.objects.filter(name__iexact="cotton", farmer__pk=farmer_pk).aggregate(
                            remaining_quantity=(Coalesce(Sum('harvest_income__quantity_sold_fpo'), 0) - Coalesce(Sum('harvest_income__quantity_sold_outside'), 0))
                            )
            total_ginned = Ginning.objects.filter(selected_farmers__farmer__in=[farmer]).exclude(ginning_status__status__in=[GinningStatus.QC_REJECTED])\
                                    .aggregate(total_ginned=Coalesce(Sum('selected_farmers__quantity'), 0.0))['total_ginned']
            if (organic_crop['remaining_quantity'] - total_ginned) < distinct_farmer_quantity_mapping[farmer_pk]:
                validation_errors.append(ValidationError(f"Total quantity entered is greater than the \
                                                          total quantity available for the Farmer \"{farmer}\""))
        if validation_errors:
            raise ValidationError(validation_errors)


SelectFarmerFormSet = formset_factory(
    SelectFarmerForm, extra=0, formset=SelectFarmerFormSet, min_num=1)


######################### Ginning Forms::END ################################


######################### Spinning Forms::BEGIN ################################
class CustomGinningModelChoiceField(ModelChoiceField):

    def label_from_instance(self, obj):
        return f'{obj.vendor} ({round(obj.remaining_quantity, 2)} Kg)'


class SelectGinningForm(ModelForm):

    subquery = Ginning.objects.filter(
        selected_ginnings__spinnings__spinning_status__status=SpinningStatus.QC_REJECTED
    ).annotate(rejected_quantity=Coalesce(Sum("selected_ginnings__quantity"), 0.0))

    ginning = CustomGinningModelChoiceField(
        label="Ginner",
        required=True,
        queryset=Ginning.objects.filter(
            ginning_status__status=GinningStatus.QC_APPROVED
        ).annotate(
            sum_quantity=Coalesce(Sum("selected_ginnings__quantity"), 0.0),
            remaining_quantity=ExpressionWrapper(
                F("ginning_outbound__quantity")
                - F("sum_quantity")
                + Coalesce(
                    Sum(
                        "selected_ginnings__quantity",
                        filter=Q(
                            selected_ginnings__spinnings__spinning_status__status=SpinningStatus.QC_REJECTED
                        ),
                    ),
                    0.0,
                ),
                output_field=_FloatField(),
            ),
        ),
        widget=Select(attrs={"class": "form-control"}),
    )

    quantity = PositiveIntegerField(required=True, widget=NumberInput(attrs={
        'class': 'form-control'
    }))

    price = PositiveIntegerField(widget=NumberInput(attrs={
        'class': 'form-control'
    }))

    invoice_no = CharField(required=True, widget=TextInput(
        attrs={
            'class': 'form-control'
        }
    ))

    lot_no = CharField(required=True, widget=TextInput(
        attrs={
            'class': 'form-control'
        }
    ))

    lint_cotton_tc_no = CharField(required=True, widget=TextInput(
        attrs={
            'class': 'form-control'
        }
    ))

    class Meta:
        model = SelectedGinning
        exclude = ['id']


class SelectGinningFormSet(BaseFormSet):
    
    def clean(self):
        """Checks that no two selected ginning farmer are same."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        distinct_ginning_quantity_mapping = {}
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            ginning = form.cleaned_data.get("ginning")
            quantity = form.cleaned_data.get("quantity")
            if ginning:
                try:
                    distinct_ginning_quantity_mapping[str(ginning.pk)] += quantity
                except KeyError:
                    distinct_ginning_quantity_mapping[str(ginning.pk)] = quantity
        validation_errors = []
        for ginning_pk in distinct_ginning_quantity_mapping.keys():
            ginning = Ginning.objects.annotate(
                sum_quantity=Coalesce(Sum('selected_ginnings__quantity'), 0.0),
                remaining_quantity=ExpressionWrapper(
                    F('ginning_outbound__quantity') - F('sum_quantity') + Coalesce(Sum('selected_ginnings__quantity', 
                                                                        filter=Q(selected_ginnings__spinnings__spinning_status__status=SpinningStatus.QC_REJECTED)), 0.0),
                    output_field=_FloatField()
                )).filter(
                pk=ginning_pk, ginning_status__status=GinningStatus.QC_APPROVED).first()
            if round(ginning.remaining_quantity, 2) < distinct_ginning_quantity_mapping[ginning_pk]:
                validation_errors.append(ValidationError(f"Total quantity entered is greater than the \
                                                          total quantity available for the ginning \"{ginning}\""))
        if validation_errors:
            raise ValidationError(validation_errors)


SelectGinningFormSet = formset_factory(
    SelectGinningForm, extra=0, formset=SelectGinningFormSet, min_num=1)


class SpinningInProcessForm(BaseCreationForm):
    timestamp = DateTimeField(required=True, label="Outbound Timestamp", widget=DateTimeInput(attrs={
        'class': 'form-control datetimepicker-input-time',
    }))
    class Meta:
        model = SpinningInProcess
        fields = ['name', 'raw_material_qty', 'output_yarn_qty']


class SpinningOutboundForm(BaseCreationForm): 
    timestamp = DateTimeField(required=True, label="Outbound Timestamp", widget=DateTimeInput(attrs={
        'class': 'form-control datetimepicker-input-time',
    }))
    class Meta:
        model = SpinningOutbound
        fields = ['invoice_no', 'timestamp',
                  'product_name', 'lot_no', 'quantity']
    def clean(self):
        quantity = self.cleaned_data['quantity']
        spinning = Spinning.objects.get(pk=self.kwargs['pk'])
        if spinning:
            if quantity > spinning.total_quantity:
                self.add_error('quantity', ValidationError("Quantity cannot be greater than total ginning quantity"))


class SpinningQualityCheckForm(BaseCreationForm):
    status = ChoiceField(label="Quality Check Status",
            choices=[(SpinningStatus.QC_APPROVED, "Approved"),
                    (SpinningStatus.QC_REJECTED, 'Rejected'),],
            widget=Select(
                attrs={
                    'class': 'form-control'
                }
            ))
    class Meta:
        model = SpinningStatus
        fields = ['actual_count', 'csp', 'rkm', 'ipi', 'status']

######################### Spinning Forms::END ################################

class GinningInProcessForm(BaseCreationForm):
    timestamp = DateTimeField(required=True, label="Outbound Timestamp", widget=DateTimeInput(attrs={
        'class': 'form-control datetimepicker-input-time',
    }))
    class Meta:
        model = GinningInProcess
        fields = ['name', 'timestamp', 'heap_no', 'consumed_qty', 'lint_qty']


class GinningOutboundForm(BaseCreationForm):
        
    timestamp = DateTimeField(required=True, label="Outbound Timestamp", widget=DateTimeInput(attrs={
        'class': 'form-control datetimepicker-input-time',
    }))
    class Meta:
        model = GinningOutbound
        fields = ['timestamp', 'invoice_no', 'product_name', 'outward_lot_no', 'quantity']
        
    def clean(self):
        quantity = self.cleaned_data['quantity']
        ginning = Ginning.objects.get(pk=self.kwargs['pk'])
        if ginning:
            if quantity > ginning.total_quantity:
                self.add_error('quantity', ValidationError("Quantity cannot be greater than total ginning quantity"))


class GinningQualityCheckForm(BaseCreationForm):
    status = ChoiceField(label="Quality Check Status",
                         choices=[(GinningStatus.QC_APPROVED, "Approved"),
                                  (GinningStatus.QC_REJECTED, 'Rejected'),],
                         widget=Select(
                             attrs={
                                 'class': 'form-control'
                             }
                         ))
    class Meta:
        model = GinningStatus
        exclude = ['ginning']


class VendorCreateForm(BaseCreationForm):
    class Meta:
        model = Vendor
        exclude = ['id']


class GinningVendorMappingForm(Form):

    vendor = ModelChoiceField(required=True, queryset=Vendor.objects.filter(is_active=True, role=Vendor.GINNING_VENDOR), widget=Select(
        attrs={
            'class': 'form-control'
        }
    ))

class SpinningVendorMappingForm(Form):

    vendor = ModelChoiceField(required=True, queryset=Vendor.objects.filter(is_active=True, role=Vendor.SPINNING_VENDOR), widget=Select(
        attrs={
            'class': 'form-control'
        }
    ))

class SeasonCreateForm(BaseCreationForm):
    class Meta:
        model = Season
        fields = '__all__'
class CostsCreateForm(BaseCreationForm):
    class Meta:
        model = Costs
        fields = '__all__'


class BulkUploadForm(BaseCreationForm):
    upload_document = FileField(required=True, widget=FileInput(attrs={
        'class': 'form-control form-control-solid ps-13'
    }))
    class Meta:
        model = BulkUpload
        fields = ['upload_document']


class BulkUploadEmailListForm(BaseCreationForm):
    class Meta:
        model = ApplicationConfiguration
        fields = ['value']
