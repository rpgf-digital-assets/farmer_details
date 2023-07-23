from django.urls import path
from . import views

app_name = 'api_farmer_admin'

urlpatterns = [
    path('delete/farmer/', views.DeleteFarmerAPIView.as_view(), name='farmer_delete_api_view'),
    path('farmer_land/coordinates/', views.FarmerLandCoordinatesAPIView.as_view(), name='farmers_land_coordinates_api_view'),
    path('farmer/<uuid:pk>/details/', views.FarmerDetailsAPIView.as_view(), name='farmer_details_api_view'),
    path('farmer/<uuid:pk>/organic_crop/generate_pdf/', views.FarmerOrganicCropGeneratePDFAPIView.as_view(), name="farmer_organic_crop_generate_pdf_api_view" ),
    
    path('delete/vendor/', views.DeleteVendorAPIView.as_view(), name='vendor_delete_api_view'),
    
    path('season/delete/', views.DeleteSeasonAPIView.as_view(), name='season_delete_api_view'),
    
    path('delete/organic_crop/', views.DeleteOrganicCropAPIView.as_view(), name='delete_organic_crop_api_view'),
    
]
