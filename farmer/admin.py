from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from farmer.models import Farmer, HistoricalFarmer

app_models = apps.get_app_config('farmer').get_models()

class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ['is_active']
    

for model in app_models:
    try:
        if model == Farmer or model == HistoricalFarmer:
            admin.site.register(model)
        else:
            admin.site.register(model, BaseModelAdmin)
    except AlreadyRegistered:
        pass