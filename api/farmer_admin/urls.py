from django.urls import path
from . import views

app_name = 'api_farmer_admin'

urlpatterns = [
    path('delete/farmer/', views.DeleteFarmerAPIView.as_view(), name='farmer_delete_api_view'),
    path('farmer_land/coordinates/', views.FarmerLandCoordinatesAPIView.as_view(), name='farmers_land_coordinates_api_view'),
    path('farmer/<uuid:pk>/details/', views.FarmerDetailsAPIView.as_view(), name='farmer_details_api_view'),
    path('farmer/<uuid:pk>/organic_crop/generate_pdf/', views.FarmerOrganicCropGeneratePDFAPIView.as_view(), name="farmer_organic_crop_generate_pdf_api_view" ),
    
    path('delete/other_farmer/', views.DeleteOtherFarmerAPIView.as_view(), name="other_farmer_delete_api_view"),
    
    path('delete/vendor/', views.DeleteVendorAPIView.as_view(), name='vendor_delete_api_view'),
    
    path('season/delete/', views.DeleteSeasonAPIView.as_view(), name='season_delete_api_view'),
    path('costs/delete/', views.DeleteCostsAPIView.as_view(), name='costs_delete_api_view'),
    path('get_costs/', views.GetCostsAPIView.as_view(), name='get_costs'),
    
    path('delete/organic_crop/', views.DeleteOrganicCropAPIView.as_view(), name='delete_organic_crop_api_view'),

    path('dashboard/crop_names/', views.GetCropNamesAPIView.as_view(), name="get_crop_names_api_view"),
    path('dashboard/crop_details_from_name/', views.GetCropDetailsFromNameAPIView.as_view(), name="get_crop_details_from_name_api_view"),
    path('dashboard/farmer_line_graph/', views.GetarmerLineGraphData.as_view(), name='get_farmer_line_graph_data_api_view'),
    path('dashboard/crop_cost_bar_graph/', views.GetCropBarGraphDetails.as_view(), name="get_crop_bar_graph_details_api_view"),
]
