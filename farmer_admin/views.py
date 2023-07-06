import os 
import folium
from PIL import Image
from io import BytesIO
from django.conf import settings

from django.core.files.base import ContentFile
from django.conf import settings
from django.db import transaction
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

from farmer.models import Farmer, FarmerLand, FarmerSocial
from farmer_admin.forms import FarmerCreationForm, FarmerLandDetailsCreationFrom, FarmerSocialCreationFrom
from users.models import User
from django.core.files.storage import FileSystemStorage


# Create your views here.

class FarmersListView(ListView):
    queryset = Farmer.objects.prefetch_related('land')
    context_object_name = 'farmers'
    template_name = 'farmer_admin/farmers_list.html'
    
    

class FarmerCreateView(CreateView):
    model = Farmer
    template_name = 'farmer_admin/farmer_create_edit.html'
    form_class = FarmerCreationForm
    success_url = reverse_lazy('farmer_admin:farmers_list')
    
    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        with transaction.atomic():
            user = User.objects.create(first_name=cleaned_data['first_name'], last_name=cleaned_data['last_name'], phone=cleaned_data['phone'], role=User.FARMER)
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
                background = Image.new('RGB', (bigside, bigside), (255, 255, 255, 255))
                offset = (int(round(((bigside - width) / 2), 0)), int(round(((bigside - height) / 2),0)))
                background.paste(img, offset)
                img_io = BytesIO()
                background.save(img_io, img.format, quality=60)
                image_file = ContentFile(img_io.getvalue(), name=image.name)
                farmer = Farmer.objects.create(user=user, profile_image=image_file, **cleaned_data)
        return redirect('farmer_admin:farmers_list')


class FarmerUpdateView(UpdateView):
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
    

class FarmerDetailsView(DetailView):
    model = Farmer
    template_name = 'farmer_admin/farmer_overview.html'
    
    

class FarmerSocialCreateView(CreateView):
    model = FarmerSocial
    template_name = 'farmer_admin/farmer_socials_create_edit.html'
    form_class = FarmerSocialCreationFrom
    success_url = reverse_lazy('farmer_admin:farmers_list')
    
    def form_valid(self, form):
        farmer = Farmer.objects.get(user__id=self.kwargs['pk'])
        form.instance.farmer = farmer 
        self.object = form.save()
        return super().form_valid(form)


class FarmerSocialUpdateView(UpdateView):
    model = FarmerSocial
    template_name = 'farmer_admin/farmer_socials_create_edit.html'
    form_class = FarmerSocialCreationFrom
    success_url = reverse_lazy('farmer_admin:farmers_list')
    context_object_name = 'farmer_social_object'


class FarmerLandDetailCreateView(CreateView):
    model = FarmerLand
    template_name = 'farmer_admin/farmer_land_details_create_edit.html'
    form_class = FarmerLandDetailsCreationFrom
    success_url = reverse_lazy('farmer_admin:farmers_list')
    
    def form_valid(self, form):
        farmer = Farmer.objects.get(user__id=self.kwargs['pk'])
        form.instance.farmer = farmer
        print("🐍 File: farmer_admin/views.py | Line: 137 | form_valid ~ form.cleaned_data['soil_test_conducted']",form.cleaned_data['soil_test_conducted'])
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


class FarmerLandDetailUpdateView(UpdateView):
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

    
class DashboardFarmerView(TemplateView):
    template_name = 'farmer_admin/dashboard_farmer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # map = folium.Map(location=[19.206217, 74.297705], zoom_start=9)
        # farmer_lands = FarmerLand.objects.all()
        average_latitude = FarmerLand.objects.aggregate(avg=Avg('latitude'))['avg']
        average_longitude = FarmerLand.objects.aggregate(avg=Avg('longitude'))['avg']
    
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
    
