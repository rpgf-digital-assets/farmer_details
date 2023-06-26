from django.urls import path
from . import views

app_name = 'api_farmer_admin'

urlpatterns = [
    path('delete/farmer/', views.DeleteFarmerAPIView.as_view(), name='farmer_delete_api_view'),
    
]
