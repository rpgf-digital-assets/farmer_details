
import os 
from PIL import Image
from io import BytesIO
from django.conf import settings

from django.core.files.base import ContentFile
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    UpdateView
)

from farmer.models import Farmer
from farmer_admin.forms import FarmerCreationForm
from users.models import User
from django.core.files.storage import FileSystemStorage


# Create your views here.

class FarmersListView(ListView):
    queryset = Farmer.objects.all()
    context_object_name = 'farmers'
    template_name = 'farmer_admin/farmers_list.html'
    

class FarmerCreateView(CreateView):
    model = Farmer
    template_name = 'farmer_admin/farmer_create.html'
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
    template_name = 'farmer_admin/farmer_create.html'
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
    
