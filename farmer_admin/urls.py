from django.urls import path
from . import views

urlpatterns = [
    path('farmer/list/', views.FarmersListView.as_view(), name='farmers_list'),
    path('farmer/create/', views.FarmerCreateView.as_view(), name='farmer_create'),    
    path('farmer/<uuid:pk>/update/', views.FarmerUpdateView.as_view(), name='farmer_update'),
    path('farmer/<uuid:pk>/overview/', views.FarmerDetailsView.as_view(), name='farmer_overview'),
    
    path('other_farmer/list/', views.OtherFarmerListView.as_view(), name="other_farmers_list"),
    path('other_farmer/create/', views.OtherFarmerCreateView.as_view(), name='other_farmer_create'),
    
    path('farmer/<uuid:pk>/social/create/', views.FarmerSocialCreateView.as_view(), name="farmer_social_create"),
    path('farmer/social/<uuid:pk>/update/', views.FarmerSocialUpdateView.as_view(), name="farmer_social_update"),
    
    path('farmer/<uuid:pk>/land_details/create/', views.FarmerLandDetailCreateView.as_view(), name="farmer_land_details_create"),
    path('farmer/land_details/<uuid:pk>/update/', views.FarmerLandDetailUpdateView.as_view(), name="farmer_land_details_update"),
    
    path('farmer/<uuid:pk>/organic_crop/create/', views.FarmerOrganicCropDetailCreateView.as_view(), name="farmer_organic_crop_create"),
    path('farmer/organic_crop/<uuid:pk>/update/', views.FarmerOrganicCropDetailUpdateView.as_view(), name="farmer_organic_crop_update"),
    
    path('farmer/<uuid:pk>/seed_details/create/', views.FarmerSeedDetailCreateView.as_view(), name="farmer_seed_details_create"),
    path('farmer/seed_details/<uuid:pk>/update/', views.FarmerSeedDetailUpdateView.as_view(), name="farmer_seed_details_update"),
    
    path('farmer/<uuid:pk>/nutrient_details/create/', views.FarmerNutrientDetailCreateView.as_view(), name="farmer_nutrient_details_create"),
    path('farmer/nutrient_details/<uuid:pk>/update/', views.FarmerNutrientDetailUpdateView.as_view(), name="farmer_nutrient_details_update"),
    
    path('farmer/<uuid:pk>/pest_disease_management/create/', views.FarmerPestDiseaseManagementCreateView.as_view(), name="farmer_pest_disease_management_create"),
    path('farmer/pest_disease_management/<uuid:pk>/update/', views.FarmerPestDiseaseManagementUpdateView.as_view(), name="farmer_pest_disease_management_update"),
    
    path('farmer/<uuid:pk>/weed_management/create/', views.FarmerWeedManagementCreateView.as_view(), name="farmer_weed_management_create"),
    path('farmer/weed_management/<uuid:pk>/update/', views.FarmerWeedManagementUpdateView.as_view(), name="farmer_weed_management_update"),
    
    path('farmer/<uuid:pk>/harvest_income/create/', views.FarmerHarvestIncomeCreateView.as_view(), name="farmer_harvest_income_create"),
    path('farmer/harvest_income/<uuid:pk>/update/', views.FarmerHarvestIncomeUpdateView.as_view(), name="farmer_harvest_income_update"),
    
    path('farmer/<uuid:pk>/cost_of_cultivation/create/', views.FarmerCostOfCultivationCreateView.as_view(), name="farmer_cost_of_cultivation_create"),
    path('farmer/cost_of_cultivation/<uuid:pk>/update/', views.FarmerCostOfCultivationUpdateView.as_view(), name="farmer_cost_of_cultivation_update"),
    
    path('farmer/<uuid:pk>/contamination_control/create/', views.FarmerContaminationControlCreateView.as_view(), name="farmer_contamination_control_create"),
    path('farmer/contamination_control/<uuid:pk>/update/', views.FarmerContaminationControlUpdateView.as_view(), name="farmer_contamination_control_update"),
    
    
    path('vendor/list/', views.VendorListView.as_view(), name="vendor_list"),
    path('vendor/create/', views.VendorCreateView.as_view(), name="vendor_create"),
    path('vendor/<uuid:pk>/update/', views.VendorUpdateView.as_view(), name="vendor_update"),
    
    
    path('traceability/ginning_mapping/create/', views.GinningMappingCreateWizardView.as_view(), name="traceability_ginning_mapping_create"),
    
    
    path('season/list/', views.SeasonListView.as_view(), name="season_list"),
    path('season/create/', views.SeasonCreateView.as_view(), name="season_create"),
    path('season/<uuid:pk>/update/', views.SeasonUpdateView.as_view(), name="season_update"),
    
    
    
    path('dashboard/farmer/', views.DashboardFarmerView.as_view(), name="dashboard_farmer_view"),
    
    path('dashboard/vendor/', views.DashboardVendorView.as_view(), name="dashboard_vendor"),
]
