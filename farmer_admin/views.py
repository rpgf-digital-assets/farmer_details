from typing import Any
from PIL import Image
from io import BytesIO
from django.conf import settings

from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.forms import Form, ValidationError
from django.http import HttpResponse
from django.db.models import Avg
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    UpdateView,
    DetailView
)

from farmer.models import ContaminationControl, CostOfCultivation, Farmer, FarmerLand, FarmerSocial, HarvestAndIncomeDetails, NutrientManagement, OrganicCropDetails, OtherFarmer, PestDiseaseManagement, Season, SeedDetails, WeedManagement
from farmer_admin.forms import ContaminationControlForm, ContaminationControlFormSet, CostOfCultivationForm, CostOfCultivationFormSet, FarmerCreationForm, FarmerLandDetailsCreationFrom, FarmerNutritionManagementForm, FarmerNutritionManagementFormSet, FarmerOrganicCropDetailForm, FarmerPestDiseaseManagementForm, FarmerPestDiseaseManagementFormSet, FarmerSeedDetailsForm, FarmerSeedDetailsFormSet, FarmerSocialCreationFrom, GinningMappingForm, HarvestAndIncomeDetailForm, HarvestAndIncomeDetailFormSet, OtherFarmerCreationForm, SeasonCreateForm, SelectedGinningFarmerForm, SelectedGinningFarmerFormSet, VendorCreateForm, WeedManagementForm, WeedManagementFormSet
from farmer_admin.mixins import AdminRequiredMixin
from farmer_details_app.mixins import CustomLoginRequiredMixin
from farmer_details_app.models import GinningMapping, SelectedGinningFarmer, Vendor
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


class FarmerSocialCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = FarmerSocial
    template_name = 'farmer_admin/farmer_socials_create_edit.html'
    form_class = FarmerSocialCreationFrom


class FarmerSocialUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = FarmerSocial
    template_name = 'farmer_admin/farmer_socials_create_edit.html'
    form_class = FarmerSocialCreationFrom
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_social_object'


class FarmerLandDetailCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = FarmerLand
    template_name = 'farmer_admin/farmer_land_details_create_edit.html'
    form_class = FarmerLandDetailsCreationFrom
    success_url = reverse_lazy('farmer_admin:farmers_list')

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
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_land_object'

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


class FarmerOrganicCropDetailCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, SessionWizardView):

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
                errors = form_list[8]._errors.setdefault(
                    forms.NON_FIELD_ERRORS, ErrorList())
                errors.append(e)
                self.render_revalidation_failure(3, form_list[8], **kwargs)

        return render(self.request, 'farmer_admin/farmer_organic_wizard/farmer_organic_wizard_done.html', {
            'form_data': [form.cleaned_data for form in form_list],
            'farmer_pk': self.kwargs['pk'],
            'completed': True,
        })


class FarmerOrganicCropDetailUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = OrganicCropDetails
    template_name = 'farmer_admin/farmer_organic_crop_create_edit.html'
    form_class = FarmerOrganicCropDetailForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_organic_object'


class FarmerOrganicCropDetailsView(CustomLoginRequiredMixin, AdminRequiredMixin, TemplateView):
    # model = OrganicCropDetails
    template_name = 'farmer_admin/farmer_organic_crop_details.html'
    # context_object_name = 'crop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["crop"] = OrganicCropDetails.objects.get(id=self.kwargs["pk"])
        return context


class FarmerSeedDetailCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = SeedDetails
    template_name = 'farmer_admin/farmer_seed_detail_create_edit.html'
    form_class = FarmerSeedDetailsForm


class FarmerSeedDetailUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = SeedDetails
    template_name = 'farmer_admin/farmer_seed_detail_create_edit.html'
    form_class = FarmerSeedDetailsForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_seed_object'


class FarmerNutrientDetailCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = NutrientManagement
    template_name = 'farmer_admin/farmer_nutrient_create_edit.html'
    form_class = FarmerNutritionManagementForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    source_field_name = 'souce_of_fertilizer'

    def form_valid(self, form):
        organic_crop = OrganicCropDetails.objects.get(user__id=self.kwargs['pk'])
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


class FarmerNutrientDetailUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = NutrientManagement
    template_name = 'farmer_admin/farmer_nutrient_create_edit.html'
    form_class = FarmerNutritionManagementForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_nutrient_object'
    source_field_name = 'souce_of_fertilizer'

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
    success_url = reverse_lazy('farmer_admin:farmers_list')
    source_field_name = 'souce_of_input'


class FarmerPestDiseaseManagementUpdateView(FarmerNutrientDetailUpdateView):
    model = PestDiseaseManagement
    template_name = 'farmer_admin/farmer_pest_management_create_update.html'
    form_class = FarmerPestDiseaseManagementForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_pest_object'
    source_field_name = 'souce_of_input'


class FarmerWeedManagementCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = WeedManagement
    template_name = 'farmer_admin/farmer_weed_create_update.html'
    form_class = WeedManagementForm


class FarmerWeedManagementUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = WeedManagement
    template_name = 'farmer_admin/farmer_weed_create_update.html'
    form_class = WeedManagementForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_weed_object'


class FarmerHarvestIncomeCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = HarvestAndIncomeDetails
    template_name = 'farmer_admin/farmer_harvest_create_update.html'
    form_class = HarvestAndIncomeDetailForm


class FarmerHarvestIncomeUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = HarvestAndIncomeDetails
    template_name = 'farmer_admin/farmer_harvest_create_update.html'
    form_class = HarvestAndIncomeDetailForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_harvest_object'


class FarmerCostOfCultivationCreateView(CustomLoginRequiredMixin, AdminRequiredMixin, BaseFarmerDetailsCreateView):
    model = CostOfCultivation
    template_name = 'farmer_admin/farmer_cost_cultivation_create_update.html'
    form_class = CostOfCultivationForm


class FarmerCostOfCultivationUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = CostOfCultivation
    template_name = 'farmer_admin/farmer_cost_cultivation_create_update.html'
    form_class = CostOfCultivationForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
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


class FarmerContaminationControlUpdateView(CustomLoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = ContaminationControl
    template_name = 'farmer_admin/farmer_contamination_control_create_update.html'
    form_class = ContaminationControlForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
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


class GinningMappingCreateWizardView(CustomLoginRequiredMixin, AdminRequiredMixin, SessionWizardView):
    form_list = [SelectedGinningFarmerFormSet, GinningMappingForm, Form]
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
            ginning_mapping = GinningMapping.objects.create(
                vendor=cleaned_data_form_2['vendor'], status=GinningMapping.IN_PROGRESS)
            for cleaned_data in cleaned_data_form_1:
                try:
                    cleaned_data['quantity']
                    ginning_mapping.selected_farmers.add(
                        SelectedGinningFarmer.objects.create(**cleaned_data))
                except KeyError:
                    pass

        return render(self.request, 'farmer_admin/ginning_mapping_wizard/ginning_mapping_wizard_done.html', {
            'form_data': [form.cleaned_data for form in form_list],
            'completed': True,
        })


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


class DashboardVendorView(CustomLoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'farmer_admin/dashboard_vendor.html'
    queryset = GinningMapping.objects.all().prefetch_related('selected_farmers')
    context_object_name = 'ginning_mappings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_mapping_count"] = GinningMapping.objects.filter(
            status=GinningMapping.IN_PROGRESS).count()
        context["completed_mapping_count"] = GinningMapping.objects.filter(
            status=GinningMapping.COMPLETED).count()
        return context


class DashboardFarmerView(TemplateView):
    template_name = 'farmer_admin/dashboard_farmer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # map = folium.Map(location=[19.206217, 74.297705], zoom_start=9)
        # farmer_lands = FarmerLand.objects.all()
        average_latitude = FarmerLand.objects.aggregate(avg=Avg('latitude'))[
            'avg']
        average_longitude = FarmerLand.objects.aggregate(avg=Avg('longitude'))[
            'avg']

        # for farmer_land in farmer_lands:
        #     farmer_details_url = reverse('farmer_admin:farmer_overview', kwargs={'pk': farmer_land.farmer.pk})
        #     html = f"""
        #     <div class=''>
        #         <a target='_blank' href='{farmer_details_url}'> Farmer </a>
        #     </div>
        #     """
        #     pp = folium.Html(html, script=True)
        #     popup = folium.Popup(pp, max_width=400)
        #     coordinates = (farmer_land.latitude, farmer_land.longitude)
        #     folium.Marker(coordinates, popup=popup).add_to(map)
        # context["map"] = map._repr_html_()
        context["average_latitude"] = average_latitude
        context["average_longitude"] = average_longitude
        return context
