import io
import json
import csv
from typing import Any
from PIL import Image
from io import BytesIO
from django.conf import settings

from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.forms import Form, ValidationError
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.db.models import Avg
from django.db.models import Sum
from django.db.models import Count
from django.db.models.functions.comparison import Coalesce
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    View,
    TemplateView,
    CreateView,
    ListView,
    FormView,
    UpdateView,
    DetailView
)

from farmer.models import ContaminationControl, CostOfCultivation, Costs, Farmer, FarmerLand, FarmerOrganicCropPdf, FarmerSocial, HarvestAndIncomeDetails, NutrientManagement, OrganicCropDetails, OtherFarmer, PestDiseaseManagement, Season, SeedDetails, WeedManagement
from farmer_admin.forms import BulkUploadEmailListForm, BulkUploadForm, ContaminationControlForm, ContaminationControlFormSet, CostOfCultivationForm, CostOfCultivationFormSet, CostsCreateForm, FarmerCreationForm, FarmerLandDetailsCreationFrom, FarmerNutritionManagementForm, FarmerNutritionManagementFormSet, FarmerOrganicCropDetailForm, FarmerPestDiseaseManagementForm, FarmerPestDiseaseManagementFormSet, FarmerSeedDetailsForm, FarmerSeedDetailsFormSet, FarmerSocialCreationFrom, GinningInProcessForm, GinningOutboundForm, GinningQualityCheckForm, SelectGinningFormSet, SpinningInProcessForm, SpinningOutboundForm, SpinningQualityCheckForm, SpinningVendorMappingForm, GinningVendorMappingForm, HarvestAndIncomeDetailForm, HarvestAndIncomeDetailFormSet, OtherFarmerCreationForm, SeasonCreateForm, SelectFarmerFormSet, VendorCreateForm, WeedManagementForm, WeedManagementFormSet
from farmer_admin.mixins import AdminRequiredMixin
from farmer_admin.tasks import validate_bulk_upload
from farmer_admin.utils import generate_certificate, get_lookup_fields, get_model_field_names, qs_to_dataset
from farmer_details_app.mixins import CustomLoginRequiredMixin
from farmer_details_app.models import ApplicationConfiguration, BulkUpload, Ginning, GinningInProcess, GinningOutbound, GinningStatus, SelectedGinning, SelectedGinningFarmer, Spinning, SpinningInProcess, SpinningOutbound, SpinningStatus, Vendor
from users.models import User
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render
from formtools.wizard.views import SessionWizardView

from django.forms import forms
from django.forms.utils import ErrorList

# Create your views here.


class BaseFarmerDetailsCreateView(CreateView):
    def get_success_url(self):
        return reverse('farmer_admin:farmer_organic_crop_details', kwargs={'pk': self.kwargs['pk']})
    
    def form_valid(self, form):
        organic_crop = OrganicCropDetails.objects.get(id=self.kwargs['pk'])
        form.instance.organic_crop = organic_crop
        self.object = form.save()
        return super().form_valid(form)
    
class BaseFarmerDetailsUpdateView(UpdateView):
    def get_success_url(self):
        instance = self.get_object()
        return reverse('farmer_admin:farmer_organic_crop_details', kwargs={'pk': instance.organic_crop.pk})


class FarmersListView(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    queryset = Farmer.objects.filter(
        user__is_active=True).prefetch_related('land')
    context_object_name = 'farmers'
    template_name = 'farmer_admin/farmers_list.html'


class FarmerCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Farmer
    template_name = 'farmer_admin/farmer_create_edit.html'
    form_class = FarmerCreationForm
    success_url = reverse_lazy('farmer_admin:farmers_list')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        with transaction.atomic():
            user = User.objects.create(
                first_name=cleaned_data['first_name'], last_name=cleaned_data['last_name'], phone=cleaned_data['phone'], role=User.FARMER)
            user.set_password(settings.DEFAULT_PASSWORD)
            user.save()
            image = cleaned_data['profile_image']

            del cleaned_data['user']
            del cleaned_data['first_name']
            del cleaned_data['last_name']
            del cleaned_data['phone']
            del cleaned_data['profile_image']

            try:
                if image.endswith('blank-profile-picture.png'):
                    farmer = Farmer.objects.create(user=user, **cleaned_data)
            except:
                img = Image.open(image)
                width, height = img.size
                bigside = max(width, height)
                background = Image.new(
                    'RGB', (bigside, bigside), (255, 255, 255, 255))
                offset = (int(round(((bigside - width) / 2), 0)),
                          int(round(((bigside - height) / 2), 0)))
                background.paste(img, offset)
                img_io = BytesIO()
                background.save(img_io, img.format, quality=60)
                image_file = ContentFile(img_io.getvalue(), name=image.name)
                farmer = Farmer.objects.create(
                    user=user, profile_image=image_file, **cleaned_data)
        return redirect('farmer_admin:farmers_list')


class FarmerUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Farmer
    template_name = 'farmer_admin/farmer_create_edit.html'
    form_class = FarmerCreationForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_object'

    def get_initial(self):
        initial = super().get_initial()
        farmer = self.get_object()
        initial['first_name'] = farmer.user.first_name
        initial['last_name'] = farmer.user.last_name
        initial['phone'] = farmer.user.phone
        return initial

    def form_valid(self, form):
        redirect_url = super(FarmerUpdateView, self).form_valid(form)
        form_data = form.cleaned_data
        user = self.get_object().user
        user.first_name = form_data['first_name']
        user.last_name = form_data['last_name']
        user.phone = form_data['phone']
        user.save()
        return redirect_url



class FarmerDetailsView(CustomLoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Farmer
    template_name = 'farmer_admin/farmer_overview.html'


class OtherFarmerListView(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    queryset = OtherFarmer.objects.filter(is_active=True)
    context_object_name = 'other_farmers'
    template_name = 'farmer_admin/other_farmers_list.html'


class OtherFarmerCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = OtherFarmer
    template_name = 'farmer_admin/other_farmer_create_edit.html'
    form_class = OtherFarmerCreationForm
    success_url = reverse_lazy('farmer_admin:farmers_list')


class OtherFarmerUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = OtherFarmer
    template_name = 'farmer_admin/other_farmer_create_edit.html'
    form_class = OtherFarmerCreationForm
    success_url = reverse_lazy('farmer_admin:other_farmers_list')
    context_object_name = 'other_farmer'
     

class FarmerSocialCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = FarmerSocial
    template_name = 'farmer_admin/farmer_socials_create_edit.html'
    form_class = FarmerSocialCreationFrom

    def form_valid(self, form):
        farmer = Farmer.objects.get(user__id=self.kwargs['pk'])
        form.instance.farmer = farmer
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('farmer_admin:farmer_overview', kwargs={'pk': self.kwargs['pk']})


class FarmerSocialUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = FarmerSocial
    template_name = 'farmer_admin/farmer_socials_create_edit.html'
    form_class = FarmerSocialCreationFrom
    context_object_name = 'farmer_social_object'
    
    def get_success_url(self):
        instance = self.get_object()
        return reverse('farmer_admin:farmer_overview', kwargs={'pk': instance.farmer.pk})


class FarmerLandDetailCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = FarmerLand
    template_name = 'farmer_admin/farmer_land_details_create_edit.html'
    form_class = FarmerLandDetailsCreationFrom
    
    def get_success_url(self):
        return reverse('farmer_admin:farmer_overview', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        farmer = Farmer.objects.get(user__id=self.kwargs['pk'])
        form.instance.farmer = farmer
        if not form.cleaned_data['soil_test_conducted']:
            form.instance.last_conducted = None
            form.instance.soil_type = None
            form.instance.soil_texture = None
            form.instance.soil_organic_matter = None
            form.instance.soil_ph = None
            form.instance.soil_drainage = None
            form.instance.soil_moisture = None
        self.object = form.save()
        return super().form_valid(form)


class FarmerLandDetailUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = FarmerLand
    template_name = 'farmer_admin/farmer_land_details_create_edit.html'
    form_class = FarmerLandDetailsCreationFrom
    context_object_name = 'farmer_land_object'
    
    def get_success_url(self):
        instance = self.get_object()
        return reverse('farmer_admin:farmer_overview', kwargs={'pk': instance.farmer.pk})

    def form_valid(self, form):
        if not form.cleaned_data['soil_test_conducted']:
            form.instance.last_conducted = None
            form.instance.soil_type = None
            form.instance.soil_texture = None
            form.instance.soil_organic_matter = None
            form.instance.soil_ph = None
            form.instance.soil_drainage = None
            form.instance.soil_moisture = None
        self.object = form.save()
        return super().form_valid(form)
    

class FarmerOrganicCropDetailCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = OrganicCropDetails
    form_class = FarmerOrganicCropDetailForm
    template_name = 'farmer_admin/farmer_organic_crop_create_edit.html'
    
    def get_success_url(self):
        return reverse('farmer_admin:farmers_list')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        farmer = Farmer.objects.get(user__id=self.kwargs['pk'])
        form.instance.farmer = farmer
        self.object = form.save(commit=False)
        farmer_land = FarmerLand.objects.get(farmer=farmer)
        total_organic_crop_area = OrganicCropDetails.objects.filter(
            is_active=True, season=cleaned_data['season'], year=cleaned_data['year'], 
            farmer=farmer
        ).aggregate(
            total_organic_crop_area=Coalesce(Sum('area'), 0.0)
        )['total_organic_crop_area']
        # total_organic_crop_area = sum([item.area for item in organic_crops])
        if int(farmer_land.total_organic_land) < int(total_organic_crop_area + cleaned_data['area']):
            form.add_error('area', ValidationError("Farmer land area is less than the organic crop area"))
            return super().form_invalid(form)   
        return super().form_valid(form)

class FarmerOrganicCropDetailSessionWizardView(CustomLoginRequiredMixin, AdminRequiredMixin, SessionWizardView):

    template_name = 'farmer_admin/farmer_organic_wizard/farmer_organic_wizard_base.html'
    form_list = [FarmerOrganicCropDetailForm,
                 FarmerSeedDetailsFormSet,
                 FarmerNutritionManagementFormSet,
                 FarmerPestDiseaseManagementFormSet,
                 WeedManagementFormSet,
                 HarvestAndIncomeDetailFormSet,
                 CostOfCultivationFormSet,
                 ContaminationControlFormSet,
                 Form]

    def dispatch(self, request, *args, **kwargs):
        farmer = Farmer.objects.get(user__id=self.kwargs['pk'])
        if farmer.land.all().count() == 0:
            messages.warning(
                request, "Land details must be added before creating crop details")
            return redirect(reverse('farmer_admin:farmer_land_details_create', kwargs={"pk": farmer.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        
        context = super().get_context_data(form=form, **kwargs)
        
        # Check if the current step should be skipped based on the flag in the session.
        # context['skip_current_step'] = self.storage.extra_data.get('skip_step', False)

        if self.steps.current != '0':
            context.update({
                'crop_name': self.get_cleaned_data_for_step('0')['name'],
                'crop_type': self.get_cleaned_data_for_step('0')['type']
            })
        if self.steps.current == '8':
            form_list = []
            form_names = [
                "Organic Crop",
                "Seed Details",
                "Nutrition Management",
                "Pest Disease Management",
                "Weed Management",
                "Harvest and Income Details",
                "Cost Of Cultivation",
                "Contamination Control",
            ]
            for index in range(0, 8):
                form_data = {
                    "form_title": form_names[index],
                    "form_data": self.get_cleaned_data_for_step(str(index))
                }
                form_list.append(form_data)

            context.update({
                'all_form_data': self.get_all_cleaned_data(),
                'form_list': form_list
            })

        return context

    def done(self, form_list, **kwargs):
        all_cleaned_data = [form.cleaned_data for form in form_list]
        cleaned_data_form_0 = all_cleaned_data[0]
        cleaned_data_form_1 = all_cleaned_data[1]
        cleaned_data_form_2 = all_cleaned_data[2]
        cleaned_data_form_3 = all_cleaned_data[3]
        cleaned_data_form_4 = all_cleaned_data[4]
        cleaned_data_form_5 = all_cleaned_data[5]
        cleaned_data_form_6 = all_cleaned_data[6]
        cleaned_data_form_7 = all_cleaned_data[7]
        farmer_land = FarmerLand.objects.get(farmer__user__id=self.kwargs['pk'])
        if farmer_land.total_organic_land < cleaned_data_form_0['area']:
            messages.warning(self.request, "Farmer land area is less than the crop area")
            return self.render_revalidation_failure(0, form_list[0])

        with transaction.atomic():
            try:
                farmer = Farmer.objects.get(user__id=self.kwargs['pk'])
                organic_crop = OrganicCropDetails.objects.create(
                    farmer=farmer, **cleaned_data_form_0)
                for cleaned_data in cleaned_data_form_1:
                    seed = SeedDetails.objects.create(
                        organic_crop=organic_crop, **cleaned_data)
                for cleaned_data in cleaned_data_form_2:
                    if cleaned_data['source_of_fertilizer'] == NutrientManagement.ON_FARM:
                        cleaned_data['sourcing_date'] = None
                        cleaned_data['quantity_sourced'] = None
                        cleaned_data['supplier_name'] = None
                    elif cleaned_data['source_of_fertilizer'] == NutrientManagement.OUTSOURCED:
                        cleaned_data['type_of_raw_material'] = None
                        cleaned_data['quantity_used'] = None
                        cleaned_data['starting_date'] = None
                        cleaned_data['date_of_manure'] = None
                        cleaned_data['quantity_obtained'] = None
                        cleaned_data['no_of_workdays_used'] = None
                    NutrientManagement.objects.create(
                        organic_crop=organic_crop, **cleaned_data)
                for cleaned_data in cleaned_data_form_3:
                    if cleaned_data['source_of_input'] == NutrientManagement.ON_FARM:
                        cleaned_data['sourcing_date'] = None
                        cleaned_data['quantity_sourced'] = None
                        cleaned_data['supplier_name'] = None
                    elif cleaned_data['source_of_input'] == NutrientManagement.OUTSOURCED:
                        cleaned_data['type_of_raw_material'] = None
                        cleaned_data['quantity_used'] = None
                        cleaned_data['starting_date'] = None
                        cleaned_data['date_of_manure'] = None
                        cleaned_data['quantity_obtained'] = None
                        cleaned_data['no_of_workdays_used'] = None
                    PestDiseaseManagement.objects.create(
                        organic_crop=organic_crop, **cleaned_data)
                for cleaned_data in cleaned_data_form_4:
                    WeedManagement.objects.create(
                        organic_crop=organic_crop, **cleaned_data)
                for cleaned_data in cleaned_data_form_5:
                    HarvestAndIncomeDetails.objects.create(
                        organic_crop=organic_crop, **cleaned_data)
                for cleaned_data in cleaned_data_form_6:
                    CostOfCultivation.objects.create(
                        organic_crop=organic_crop, **cleaned_data)
                for cleaned_data in cleaned_data_form_7:
                    ContaminationControl.objects.create(
                        organic_crop=organic_crop, **cleaned_data)
            except Exception as e:
                print("🐍 File: farmer_admin/views.py | Line: 334 | done ~ e",e)
                errors = form_list[8]._errors.setdefault(
                    forms.NON_FIELD_ERRORS, ErrorList())
                errors.append(e)
                return self.render_revalidation_failure(8, form_list[8], **kwargs)

        return render(self.request, 'farmer_admin/farmer_organic_wizard/farmer_organic_wizard_done.html', {
            'form_data': [form.cleaned_data for form in form_list],
            'farmer_pk': self.kwargs['pk'],
            'completed': True,
        })


class FarmerOrganicCropDetailUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = OrganicCropDetails
    template_name = 'farmer_admin/farmer_organic_crop_create_edit.html'
    form_class = FarmerOrganicCropDetailForm
    context_object_name = 'farmer_organic_object'

    def get_success_url(self):
        return reverse('farmer_admin:farmer_organic_crop_details', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        farmer_land = FarmerLand.objects.get(farmer=self.get_object().farmer)
        instance = self.get_object()
        organic_crops = OrganicCropDetails.objects.filter(is_active=True, farmer=self.get_object().farmer).exclude(id=instance.pk)
        total_organic_crop_area = sum([item.area for item in organic_crops]) 
        if int(farmer_land.total_organic_land) < int(total_organic_crop_area + cleaned_data['area']):
            form.add_error('area', ValidationError("Farmer land area is less than the organic crop area"))
            return super().form_invalid(form)
        return super().form_valid(form)


class FarmerOrganicCropDetailsView(CustomLoginRequiredMixin, AdminRequiredMixin, TemplateView):
    # model = OrganicCropDetails
    template_name = 'farmer_admin/farmer_organic_crop_details.html'
    # context_object_name = 'crop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organic_crop = OrganicCropDetails.objects.filter(id=self.kwargs["pk"], is_active=True).first()
        context["crop"] = organic_crop
        return context


class FarmerSeedDetailCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = SeedDetails
    template_name = 'farmer_admin/farmer_seed_detail_create_edit.html'
    form_class = FarmerSeedDetailsForm


class FarmerSeedDetailUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsUpdateView):
    model = SeedDetails
    template_name = 'farmer_admin/farmer_seed_detail_create_edit.html'
    form_class = FarmerSeedDetailsForm
    context_object_name = 'farmer_seed_object'


class FarmerNutrientDetailCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = NutrientManagement
    template_name = 'farmer_admin/farmer_nutrient_create_edit.html'
    form_class = FarmerNutritionManagementForm
    source_field_name = 'source_of_fertilizer'

    def get_success_url(self):
        return reverse('farmer_admin:farmer_organic_crop_details', kwargs={'pk': self.kwargs['pk']})
    
    def form_valid(self, form):
        organic_crop = OrganicCropDetails.objects.get(id=self.kwargs['pk'])
        form.instance.organic_crop = organic_crop
        if form.cleaned_data[self.source_field_name] == NutrientManagement.ON_FARM:
            form.instance.sourcing_date = None
            form.instance.quantity_sourced = None
            form.instance.supplier_name = None
        elif form.cleaned_data[self.source_field_name] == NutrientManagement.OUTSOURCED:
            form.instance.type_of_raw_material = None
            form.instance.quantity_used = None
            form.instance.starting_date = None
            form.instance.date_of_manure = None
            form.instance.quantity_obtained = None
            form.instance.no_of_workdays_used = None
        self.object = form.save()
        return super().form_valid(form)


class FarmerNutrientDetailUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsUpdateView):
    model = NutrientManagement
    template_name = 'farmer_admin/farmer_nutrient_create_edit.html'
    form_class = FarmerNutritionManagementForm
    context_object_name = 'farmer_nutrient_object'
    source_field_name = 'source_of_fertilizer'

    def form_valid(self, form):
        if form.cleaned_data[self.source_field_name] == NutrientManagement.ON_FARM:
            form.instance.sourcing_date = None
            form.instance.quantity_sourced = None
            form.instance.supplier_name = None
        elif form.cleaned_data[self.source_field_name] == NutrientManagement.OUTSOURCED:
            form.instance.type_of_raw_material = None
            form.instance.quantity_used = None
            form.instance.starting_date = None
            form.instance.date_of_manure = None
            form.instance.quantity_obtained = None
            form.instance.no_of_workdays_used = None
        self.object = form.save()
        return super().form_valid(form)


class FarmerPestDiseaseManagementCreateView(FarmerNutrientDetailCreateView):
    model = PestDiseaseManagement
    template_name = 'farmer_admin/farmer_pest_management_create_update.html'
    form_class = FarmerPestDiseaseManagementForm
    source_field_name = 'source_of_input'


class FarmerPestDiseaseManagementUpdateView(FarmerNutrientDetailUpdateView):
    model = PestDiseaseManagement
    template_name = 'farmer_admin/farmer_pest_management_create_update.html'
    form_class = FarmerPestDiseaseManagementForm
    context_object_name = 'farmer_pest_object'
    source_field_name = 'source_of_input'


class FarmerWeedManagementCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = WeedManagement
    template_name = 'farmer_admin/farmer_weed_create_update.html'
    form_class = WeedManagementForm


class FarmerWeedManagementUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsUpdateView):
    model = WeedManagement
    template_name = 'farmer_admin/farmer_weed_create_update.html'
    form_class = WeedManagementForm
    context_object_name = 'farmer_weed_object'


class FarmerHarvestIncomeCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = HarvestAndIncomeDetails
    template_name = 'farmer_admin/farmer_harvest_create_update.html'
    form_class = HarvestAndIncomeDetailForm


class FarmerHarvestIncomeUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsUpdateView):
    model = HarvestAndIncomeDetails
    template_name = 'farmer_admin/farmer_harvest_create_update.html'
    form_class = HarvestAndIncomeDetailForm
    context_object_name = 'farmer_harvest_object'


class FarmerCostOfCultivationCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = CostOfCultivation
    template_name = 'farmer_admin/farmer_cost_cultivation_create_update.html'
    form_class = CostOfCultivationForm


class FarmerCostOfCultivationUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsUpdateView):
    model = CostOfCultivation
    template_name = 'farmer_admin/farmer_cost_cultivation_create_update.html'
    form_class = CostOfCultivationForm
    context_object_name = 'farmer_cost_object'


class FarmerContaminationControlCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = ContaminationControl
    template_name = 'farmer_admin/farmer_contamination_control_create_update.html'
    form_class = ContaminationControlForm

    def form_valid(self, form):
        chances = form.cleaned_data.get('chances')
        if ContaminationControl.objects.filter(organic_crop__id=self.kwargs["pk"], chances=chances).exists():
            form.add_error('chances', ValidationError('Chances already exists'))
            return super().form_invalid(form)
        return super().form_valid(form)


class FarmerContaminationControlUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsUpdateView):
    model = ContaminationControl
    template_name = 'farmer_admin/farmer_contamination_control_create_update.html'
    form_class = ContaminationControlForm
    context_object_name = 'farmer_contamination_object'

    def form_valid(self, form):
        chances = form.cleaned_data.get('chances')
        instance = self.get_object()
        if 'chances' in form.changed_data:
            # Chances changed check if it already exists
            if ContaminationControl.objects.filter(organic_crop=instance.organic_crop, chances=chances).exists():
                form.add_error('chances', ValidationError('Chances already exists'))
                return super().form_invalid(form)
        return super().form_valid(form)


class GenerateOrganicCropPdfView(CustomLoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'farmer_admin/organic_crop_pdf.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        farmer = Farmer.objects.get(user__id=self.kwargs['farmer_pk'])
        organic_crop = OrganicCropDetails.objects.filter(farmer=farmer, is_active=True)
        context["crops"] = organic_crop
        context["farmer"] = farmer
        context["farmer_land"] = farmer.land.all().first()
        context["crop_headings"] = {
            "seed": SeedDetails._meta.get_fields(),
            "nutrient": NutrientManagement._meta.get_fields(),
            "pest": PestDiseaseManagement._meta.get_fields(),
            "weed": WeedManagement._meta.get_fields(),
            "harvest": HarvestAndIncomeDetails._meta.get_fields(),
            "cost": CostOfCultivation._meta.get_fields(),
            "contamination": ContaminationControl._meta.get_fields(),
        }
        return context
    


class VendorListView(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'farmer_admin/vendor_list.html'
    queryset = Vendor.objects.filter(is_active=True)
    context_object_name = 'vendors'


class VendorCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    template_name = 'farmer_admin/vendor_create_edit.html'
    form_class = VendorCreateForm
    success_url = reverse_lazy('farmer_admin:vendor_list')


class VendorUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    template_name = 'farmer_admin/vendor_create_edit.html'
    queryset = Vendor.objects.filter(is_active=True)
    form_class = VendorCreateForm
    success_url = reverse_lazy('farmer_admin:vendor_list')
    context_object_name = 'vendor_object'


class SeasonListView(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'farmer_admin/season_list.html'
    queryset = Season.objects.filter(is_active=True)
    context_object_name = 'seasons'


class SeasonCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    form_class = SeasonCreateForm
    template_name = 'farmer_admin/season_create_edit.html'
    success_url = reverse_lazy('farmer_admin:season_list')


class SeasonUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    template_name = 'farmer_admin/season_create_edit.html'
    queryset = Season.objects.filter(is_active=True)
    form_class = SeasonCreateForm
    success_url = reverse_lazy('farmer_admin:season_list')
    context_object_name = 'season_object'


class CostsListView(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'farmer_admin/costs_list.html'
    queryset = Costs.objects.filter(is_active=True)
    context_object_name = 'costs'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        field_verbose_dict = {}
        for field in Costs._meta.get_fields():
            if field.name in ['id', 'is_active']:
                continue
            if hasattr(field, 'verbose_name'):
                field_verbose_dict[field.name] = (
                    field.verbose_name, field.get_internal_type())
        context["field_verbose_dict"] = field_verbose_dict
        context['create_url'] = 'farmer_admin:costs_create'
        context['edit_url'] = 'farmer_admin:costs_update'
        context['delete_url'] = reverse('api:api_farmer_admin:costs_delete_api_view')
        return context

class CostsCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    form_class = CostsCreateForm
    template_name = 'farmer_admin/costs_create_edit.html'
    success_url = reverse_lazy('farmer_admin:costs_list')
    


class CostsUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    template_name = 'farmer_admin/costs_create_edit.html'
    queryset = Costs.objects.filter(is_active=True)
    form_class = CostsCreateForm
    success_url = reverse_lazy('farmer_admin:costs_list')
    context_object_name = 'costs_object'
    
       
   
class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class FarmerCSV(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        output = []
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        query_set = Farmer.objects.all()
        print("🐍 File: farmer_admin/views.py | Line: 800 | get ~ query_set",query_set)
        #Header
        writer.writerow(['Name', 'gender', 'Birth Date', 'Aadhar Number', 'Registration Number', 'Date of joining the program', 
                        'village', 'taluka', 'district', 'state', 'country'])
        for farmer in query_set:
            output.append([farmer.user.user_display_name, farmer.gender, farmer.birth_date, 
                           farmer.aadhar_number, farmer.registration_number, farmer.date_of_joining_of_program,
                           farmer.village, farmer.taluka, farmer.district, farmer.state, farmer.country])
        #CSV Data
        writer.writerows(output)
        return response
    

class OtherFarmerCSV(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        output = []
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        query_set = OtherFarmer.objects.filter(is_active=True)
        #Header
        writer.writerow(['Name', 'gender', 'Owned Land', 'Identification Number', 'Latitude', 'Longitude', 
                        'village', 'taluka', 'district', 'state', 'country'])
        for farmer in query_set:
            output.append([farmer.user_display_name, farmer.gender, farmer.owned_land, 
                           farmer.identification_number, farmer.latitude, farmer.longitude,
                           farmer.village, farmer.taluka, farmer.district, farmer.state])
        #CSV Data
        writer.writerows(output)
        return response
    

class VendorCSV(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        output = []
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        query_set = Vendor.objects.filter(is_active=True)
        #Header
        writer.writerow(['Name', 'Company Name', 'Concerned Person', 'Date of Joining',
                          'Role', 'email', 'phone', 'ID type', 'Identification Number',
                         'website', 'address', 'city', 'state', 'pincode'])
        
        for vendor in query_set:
            output.append([vendor.user_display_name, vendor.company_name, vendor.concerned_person, 
                           vendor.date_of_joining, vendor.role, vendor.email,
                           vendor.phone, vendor.identification_type, vendor.identification_number, vendor.website,
                           vendor.address, vendor.city, vendor.state, vendor.pincode])
        #CSV Data
        writer.writerows(output)
        return response


class OrganicCropCsv(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        output = []
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        organic_crops = OrganicCropDetails.objects.filter(is_active=True)
        organic_crop_ids = OrganicCropDetails.objects.filter(is_active=True).values_list('id', flat=True)
        seeds = SeedDetails.objects.filter(is_active=True, organic_crop__in=organic_crop_ids).select_related('organic_crop')
        nutrients = NutrientManagement.objects.filter(is_active=True, organic_crop__in=organic_crop_ids)
        pests = PestDiseaseManagement.objects.filter(is_active=True, organic_crop__in=organic_crop_ids)
        weeds = WeedManagement.objects.filter(is_active=True, organic_crop__in=organic_crop_ids)
        harvests = HarvestAndIncomeDetails.objects.filter(is_active=True, organic_crop__in=organic_crop_ids)
        costs = CostOfCultivation.objects.filter(is_active=True, organic_crop__in=organic_crop_ids)
        contaminations = ContaminationControl.objects.filter(is_active=True, organic_crop__in=organic_crop_ids)

        # Organic crops
        writer.writerow(['Name', 'Farmer Name', "Type", "Area", "Date of sowing", "Expected date of harvest", "Expected yield in kg", "Expected productivity in kg/ha", "Season", "Season Year"])
        for organic_crop in organic_crops:
            output.append([organic_crop.name, organic_crop.farmer.user.user_display_name, organic_crop.type, organic_crop.area, organic_crop.date_of_sowing, organic_crop.expected_date_of_harvesting, organic_crop.expected_yield, organic_crop.expected_productivity, organic_crop.season.name, organic_crop.year])
        writer.writerows(output)

        model_queryset_mapping = {SeedDetails: seeds, NutrientManagement: nutrients, PestDiseaseManagement: pests, WeedManagement: weeds, 
                      HarvestAndIncomeDetails: harvests, CostOfCultivation: costs, ContaminationControl: contaminations}
        
        for model in model_queryset_mapping.keys():
            output = []
            writer.writerow([])
            fields = ['organic_crop__name', *get_model_field_names(model, ignore_fields=['id', 'is_active', 'organic_crop'])]
            writer.writerow(fields)
            dataset = qs_to_dataset(model_queryset_mapping[model], fields=fields)
            for data in dataset:
                output.append(data.values())
            writer.writerows(output)

        return response

 
class DashboardFarmerView(TemplateView):
    template_name = 'farmer_admin/dashboard_farmer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        average_latitude = FarmerLand.objects.filter(is_active=True).aggregate(avg=Avg('latitude'))[
            'avg']
        average_longitude = FarmerLand.objects.filter(is_active=True).aggregate(avg=Avg('longitude'))[
            'avg']
        context["average_latitude"] = average_latitude
        context["average_longitude"] = average_longitude

        # Total Farmer data
        context["farmers_count"] = Farmer.objects.all().count() + OtherFarmer.objects.filter(is_active=True).count()
        context["organic_crop_count"] = OrganicCropDetails.objects.filter(is_active=True).count()
        
        # Total Organic crop data
        total_organic_crop_area = OrganicCropDetails.objects.filter(is_active=True).aggregate(total_area=Sum('area'))['total_area']
        context["total_organic_crop_area"] = round(total_organic_crop_area, 3)
        
        # Piechart data
        piechart_data = OrganicCropDetails.objects.filter(is_active=True).values('name').annotate(category=Count("name"), value=Sum('area')).order_by()
        piechart_data = [[chart['name'], chart['value']] for chart in piechart_data]
        context["piechart"] = json.dumps(piechart_data)

        # Nutrition Bar graph data
        nutrient_management_fym = NutrientManagement.objects.filter(is_active=True, type=NutrientManagement.FYM) \
                                .aggregate(total_fertilizer_quantity=Sum('quantity_of_fertilizer'), 
                                            total_on_farm_quantity=Sum('quantity_used'), total_off_farm_quantity=Sum('quantity_sourced'))
        nutrient_management_vermicompost = NutrientManagement.objects.filter(is_active=True, type=NutrientManagement.VERMICOMPOST) \
                                .aggregate(total_fertilizer_quantity=Sum('quantity_of_fertilizer'), 
                                            total_on_farm_quantity=Sum('quantity_used'), total_off_farm_quantity=Sum('quantity_sourced'))
        nutrient_management_compost = NutrientManagement.objects.filter(is_active=True, type=NutrientManagement.COMPOST) \
                                .aggregate(total_fertilizer_quantity=Sum('quantity_of_fertilizer'), 
                                            total_on_farm_quantity=Sum('quantity_used'), total_off_farm_quantity=Sum('quantity_sourced'))
        nutrition_bar_graph_data = [{
            "year": "On Farm",
            "vermicompost": nutrient_management_vermicompost['total_fertilizer_quantity'],
            "vermicompost-used": nutrient_management_vermicompost['total_on_farm_quantity'],
            "compost": nutrient_management_compost['total_fertilizer_quantity'],
            "compost-used": nutrient_management_compost['total_on_farm_quantity'],
            "FYM": nutrient_management_fym['total_fertilizer_quantity'],
            "FYM-used": nutrient_management_fym['total_on_farm_quantity'],
        },{
            "year": "Outsourced",
            "vermicompost": nutrient_management_vermicompost['total_fertilizer_quantity'],
            "vermicompost-used": nutrient_management_vermicompost['total_off_farm_quantity'],
            "compost": nutrient_management_compost['total_fertilizer_quantity'],
            "compost-used": nutrient_management_compost['total_off_farm_quantity'],
            "FYM": nutrient_management_fym['total_fertilizer_quantity'],
            "FYM-used": nutrient_management_fym['total_off_farm_quantity'],
        }]

        context["nutrition_bar_graph_data"] = json.dumps(nutrition_bar_graph_data)

        # Pest and Disease Bar graph data
        pest_management_fym = PestDiseaseManagement.objects.filter(is_active=True, source_of_input=NutrientManagement.FYM) \
                                .aggregate(total_fertilizer_quantity=Sum('quantity_of_input'), 
                                            total_on_farm_quantity=Sum('quantity_used'), total_off_farm_quantity=Sum('quantity_sourced'))
        pest_management_vermicompost = PestDiseaseManagement.objects.filter(is_active=True, source_of_input=NutrientManagement.VERMICOMPOST) \
                                .aggregate(total_fertilizer_quantity=Sum('quantity_of_input'), 
                                            total_on_farm_quantity=Sum('quantity_used'), total_off_farm_quantity=Sum('quantity_sourced'))
        pest_management_compost = PestDiseaseManagement.objects.filter(is_active=True, source_of_input=NutrientManagement.COMPOST) \
                                .aggregate(total_fertilizer_quantity=Sum('quantity_of_input'), 
                                            total_on_farm_quantity=Sum('quantity_used'), total_off_farm_quantity=Sum('quantity_sourced'))
                                
        pest_management = PestDiseaseManagement.objects.filter(is_active=True) \
                                .aggregate(
                                    # total_fertilizer_quantity=Sum('quantity_of_input'), 
                                    total_on_farm_quantity=Sum('quantity_used'), 
                                    total_off_farm_quantity=Sum('quantity_sourced'))
        
        pest_piechart_data = [
            # {"value": pest_management["total_fertilizer_quantity"], "category": "Fertilizer"},
            {"value": pest_management["total_on_farm_quantity"], "category": "On Farm"},
            {"value": pest_management["total_off_farm_quantity"], "category": "Off Farm"},
        ]
        
        context["pest_piechart_data"] = json.dumps(pest_piechart_data)
        
        context['year_range'] = [i for i in range(timezone.now().year, timezone.now().year - 10, -1)]
        
        # Get Raw cotton and ginned cotton data
        context['raw_cotton'] = Ginning.objects.filter(ginning_status__status=GinningStatus.QC_APPROVED) \
                .aggregate(raw_cotton=Sum('total_quantity') - Sum('ginning_outbound__quantity'))['raw_cotton']
                
        spinned_cotton = Spinning.objects.filter(is_active=True, spinning_status__status=SpinningStatus.QC_APPROVED)\
                .aggregate(total_quantity=Sum('spinning_outbound__quantity'))
        context['ginned_cotton'] = Ginning.objects.filter(ginning_status__status=GinningStatus.QC_APPROVED) \
            .aggregate(ginned_cotton=Sum('ginning_outbound__quantity') - Coalesce(spinned_cotton['total_quantity'], 0.0))['ginned_cotton']
            
        context['yarn'] = spinned_cotton['total_quantity'] or 0
        
        return context


class GinningMappingCreateWizardView(CustomLoginRequiredMixin, AdminRequiredMixin, SessionWizardView):
    form_list = [SelectFarmerFormSet, GinningVendorMappingForm, Form]
    template_name = 'farmer_admin/ginning_mapping_wizard/ginning_mapping_wizard_base.html'

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == '2':
            context.update({
                'form_1_data': self.get_cleaned_data_for_step('0'),
                'form_2_data': self.get_cleaned_data_for_step('1')
            })
        return context

    def done(self, form_list, **kwargs):
        all_cleaned_data = [form.cleaned_data for form in form_list]
        cleaned_data_form_1 = all_cleaned_data[0]
        cleaned_data_form_2 = all_cleaned_data[1]
        with transaction.atomic():
            ginning = Ginning.objects.create(
                vendor=cleaned_data_form_2['vendor'])
            GinningStatus.objects.create(ginning=ginning)
            for cleaned_data in cleaned_data_form_1:
                try:
                    cleaned_data['quantity']
                    ginning.selected_farmers.add(
                        SelectedGinningFarmer.objects.create(**cleaned_data))
                    ginning.save()
                except KeyError:
                    pass

        return render(self.request, 'farmer_admin/ginning_mapping_wizard/ginning_mapping_wizard_done.html', {
            'form_data': [form.cleaned_data for form in form_list],
            'completed': True,
        })


class GinningListView(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'farmer_admin/ginning_list.html'
    queryset = Ginning.objects.all().prefetch_related('selected_farmers')
    context_object_name = 'ginnings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_mapping_count"] = Ginning.objects.filter(
            ginning_status__status=GinningStatus.IN_PROGRESS).count()
        context["completed_mapping_count"] = Ginning.objects.filter(
            ginning_status__status=GinningStatus.COMPLETED).count()
        return context
    
class GetGinningList(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'farmer_admin/ginning_rows.html'
    queryset = Ginning.objects.all().prefetch_related('selected_farmers')
    context_object_name = 'ginnings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_mapping_count"] = Ginning.objects.filter(
            ginning_status__status=GinningStatus.IN_PROGRESS).count()
        context["completed_mapping_count"] = Ginning.objects.filter(
            ginning_status__status=GinningStatus.COMPLETED).count()
        return context


class GinningOutboundRequest(CustomLoginRequiredMixin, AdminRequiredMixin, FormView):
    form_class = GinningOutboundForm
    template_name = 'farmer_admin/inbound_form.html'
    
    def get_form_kwargs(self):
        kw = super(GinningOutboundRequest, self).get_form_kwargs()
        kw['kwargs'] = self.kwargs # the trick!
        return kw
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_url"] = reverse(
            'farmer_admin:ginning_outbound_request_create_view', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        timestamp = form.cleaned_data.get('timestamp')
        invoice_no = form.cleaned_data.get('invoice_no')
        product_name = form.cleaned_data.get('product_name')
        outward_lot_no = form.cleaned_data.get('outward_lot_no')
        quantity = form.cleaned_data.get('quantity')

        # Create outbound request
        ginning = Ginning.objects.get(pk=self.kwargs['pk'])
        GinningOutbound.objects.update_or_create(ginning=ginning, defaults={
            "timestamp": timestamp,
            "invoice_no": invoice_no,
            "product_name": product_name,
            "outward_lot_no": outward_lot_no,
            "quantity": quantity,
        })

        # Change status
        ginning.ginning_status.status = GinningStatus.QC_PENDING
        ginning.ginning_status.save()
        ginning.save()

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})


class GinningInProcessRequest(CustomLoginRequiredMixin, AdminRequiredMixin, FormView):
    form_class = GinningInProcessForm
    template_name = 'farmer_admin/inprogress_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_url"] = reverse(
            'farmer_admin:ginning_inprocess_request_create_view', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        heap_no = form.cleaned_data.get('heap_no')
        consumed_qty = form.cleaned_data.get('consumed_qty')
        lint_qty = form.cleaned_data.get('lint_qty')

        recovery = (lint_qty / consumed_qty) * 100
        
        # Create outbound request
        ginning = Ginning.objects.get(pk=self.kwargs['pk'])
        GinningInProcess.objects.update_or_create(ginning=ginning, defaults={
            "name": name,
            "heap_no": heap_no,
            "consumed_qty": consumed_qty,
            "lint_qty": lint_qty,
            "recovery": recovery,
        })

        # Change status
        ginning.ginning_status.status = GinningStatus.IN_PROGRESS
        ginning.ginning_status.save()
        ginning.save()

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})


class GinningQcRequestCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, FormView):
    form_class = GinningQualityCheckForm
    template_name = 'farmer_admin/qc_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_url"] = reverse(
            'farmer_admin:ginning_qc_request_create_view', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        ginning = Ginning.objects.get(pk=self.kwargs['pk'])
        status = form.cleaned_data.get('status')
        length = form.cleaned_data.get('length')
        mic = form.cleaned_data.get('mic')
        strength = form.cleaned_data.get('strength')
        trash = form.cleaned_data.get('trash')
        rd_plus = form.cleaned_data.get('rd_plus')

        GinningStatus.objects.update_or_create(ginning=ginning, defaults={
            "status": status,
            "length": length,
            "mic": mic,
            "strength": strength,
            "trash": trash,
            "rd_plus": rd_plus,
        })

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})


class SpinningMappingCreateWizardView(CustomLoginRequiredMixin, AdminRequiredMixin, SessionWizardView):
    form_list = [SelectGinningFormSet, SpinningVendorMappingForm, Form]
    template_name = 'farmer_admin/spinning_mapping_wizard/spinning_mapping_wizard_base.html'

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        
        if self.steps.current == '2':
            context.update({
                'form_1_data': self.get_cleaned_data_for_step('0'),
                'form_2_data': self.get_cleaned_data_for_step('1')
            })
            
        return context

    def done(self, form_list, **kwargs):
        all_cleaned_data = [form.cleaned_data for form in form_list]
        cleaned_data_form_1 = all_cleaned_data[0]
        cleaned_data_form_2 = all_cleaned_data[1]
        with transaction.atomic():
            spinning = Spinning.objects.create(
                vendor=cleaned_data_form_2['vendor'])
            SpinningStatus.objects.create(spinning=spinning)
            for cleaned_data in cleaned_data_form_1:
                try:
                    cleaned_data['quantity']
                    spinning.selected_ginnings.add(
                        SelectedGinning.objects.create(**cleaned_data))
                except KeyError:
                    pass

        return render(self.request, 'farmer_admin/spinning_mapping_wizard/spinning_mapping_wizard_done.html', {
            'form_data': [form.cleaned_data for form in form_list],
            'completed': True,
        })


class SpinningListView(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'farmer_admin/spinning_list.html'
    queryset = Spinning.objects.all().prefetch_related('selected_ginnings')
    context_object_name = 'spinnings'
    
    
class GetSpinningList(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'farmer_admin/spinning_rows.html'
    queryset = Spinning.objects.all().prefetch_related('selected_ginnings')
    context_object_name = 'spinnings'


class SpinningInProcessRequest(CustomLoginRequiredMixin, AdminRequiredMixin, FormView):
    form_class = SpinningInProcessForm
    template_name = 'farmer_admin/inbound_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_url"] = reverse(
            'farmer_admin:spinning_inprocess_request_create_view', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        raw_material_qty = form.cleaned_data.get('raw_material_qty')
        output_yarn_qty = form.cleaned_data.get('output_yarn_qty')
        
        recovery = (output_yarn_qty / raw_material_qty) * 100

        # Create outbound request
        spinning = Spinning.objects.get(pk=self.kwargs['pk'])
        SpinningInProcess.objects.update_or_create(spinning=spinning, defaults={
            "name": name,
            "raw_material_qty": raw_material_qty,
            "output_yarn_qty": output_yarn_qty,
            "recovery": recovery,
        })

        # Change status
        spinning.spinning_status.status = SpinningStatus.IN_PROGRESS
        spinning.spinning_status.save()
        spinning.save()

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})

class SpinningOutboundRequest(CustomLoginRequiredMixin, AdminRequiredMixin, FormView):
    form_class = SpinningOutboundForm
    template_name = 'farmer_admin/inbound_form.html'
    
    def get_form_kwargs(self):
        kw = super(SpinningOutboundRequest, self).get_form_kwargs()
        kw['kwargs'] = self.kwargs # the trick!
        return kw
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_url"] = reverse(
            'farmer_admin:spinning_outbound_request_create_view', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        timestamp = form.cleaned_data.get('timestamp')
        quantity = form.cleaned_data.get('quantity')
        invoice_no = form.cleaned_data.get('invoice_no')
        lot_no = form.cleaned_data.get('lot_no')
        product_name = form.cleaned_data.get('product_name')

        # Create outbound request
        spinning = Spinning.objects.get(pk=self.kwargs['pk'])
        SpinningOutbound.objects.update_or_create(spinning=spinning, defaults={
            "timestamp": timestamp,
            "quantity": quantity,
            "product_name": product_name,
            "lot_no": lot_no,
            "invoice_no": invoice_no
        })

        # Change status
        spinning.spinning_status.status = SpinningStatus.QC_PENDING
        spinning.spinning_status.save()
        spinning.save()

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})


class SpinningQcRequestCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, FormView):
    form_class = SpinningQualityCheckForm
    template_name = 'farmer_admin/qc_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_url"] = reverse(
            'farmer_admin:spinning_qc_request_create_view', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        spinning = Spinning.objects.get(pk=self.kwargs['pk'])
        status = form.cleaned_data.get('status')
        actual_count = form.cleaned_data.get('actual_count')
        csp = form.cleaned_data.get('csp')
        rkm = form.cleaned_data.get('rkm')
        ipi = form.cleaned_data.get('ipi')

        SpinningStatus.objects.update_or_create(spinning=spinning, defaults={
            "status": status,
            "actual_count": actual_count,
            "csp": csp,
            "rkm": rkm,
            "ipi": ipi
        })

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})


class BulkUploadList(CustomLoginRequiredMixin, AdminRequiredMixin, FormView, ListView):
    form_class = BulkUploadForm
    model = BulkUpload
    template_name = 'farmer_admin/upload_csv.html'
    context_object_name = 'bulk_upload_documents'
    success_url = reverse_lazy('farmer_admin:bulk_upload_list')
    queryset = BulkUpload.objects.filter(is_active=True).order_by('-timestamp')
    
    def form_valid(self, form):
        object = form.save()
        validate_bulk_upload.delay(object.pk)
        return super(BulkUploadList, self).form_valid(form)


class BulkUploadEditEmailList(CustomLoginRequiredMixin, AdminRequiredMixin, FormView):
    form_class = BulkUploadEmailListForm
    template_name = 'farmer_admin/bulk_upload_email_edit_form.html'
    application_config_name = 'BulkUploadEmailList'
    
    def get_initial(self):
        initial = super().get_initial()
        instance = ApplicationConfiguration.objects.filter(name=self.application_config_name).first()
        if instance:
            initial['value'] = instance.value
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_url"] = reverse(
            'farmer_admin:bulk_upload_edit_email_list')
        return context

    def form_valid(self, form):
        value = form.cleaned_data.get('value')

        # Create application configuration
        ApplicationConfiguration.objects.update_or_create(name=self.application_config_name, defaults={'value': value})

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})