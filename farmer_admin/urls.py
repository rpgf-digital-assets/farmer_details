from django.urls import path
from . import views

urlpatterns = [
    path('farmer/list/', views.FarmersListView.as_view(), name='farmers_list'),
    path('farmer/create/', views.FarmerCreateView.as_view(), name='farmer_create'),    
    path('farmer/<uuid:pk>/update/', views.FarmerUpdateView.as_view(), name='farmer_update'),
    path('farmer/<uuid:pk>/overview/', views.FarmerDetailsView.as_view(), name='farmer_overview'),
    
    path('other_farmer/list/', views.OtherFarmerListView.as_view(), name="other_farmers_list"),
    path('other_farmer/create/', views.OtherFarmerCreateView.as_view(), name='other_farmer_create'),
    path('other_farmer/<uuid:pk>/update/', views.OtherFarmerUpdateView.as_view(), name='other_farmer_update'),
    
    path('farmer/<uuid:pk>/social/create/', views.FarmerSocialCreateView.as_view(), name="farmer_social_create"),
    path('farmer/social/<uuid:pk>/update/', views.FarmerSocialUpdateView.as_view(), name="farmer_social_update"),
    
    path('farmer/<uuid:pk>/land_details/create/', views.FarmerLandDetailCreateView.as_view(), name="farmer_land_details_create"),
    path('farmer/land_details/<uuid:pk>/update/', views.FarmerLandDetailUpdateView.as_view(), name="farmer_land_details_update"),
    
    path('farmer/<uuid:pk>/organic_crop/create/', views.FarmerOrganicCropDetailCreateView.as_view(), name="farmer_organic_crop_create"),
    path('farmer/organic_crop/<uuid:pk>/update/', views.FarmerOrganicCropDetailUpdateView.as_view(), name="farmer_organic_crop_update"),
    path('farmer/organic_crop/<uuid:pk>/details/', views.FarmerOrganicCropDetailsView.as_view(), name="farmer_organic_crop_details"),

    path('farmer/organic_crop/<uuid:pk>/seed_details/create/', views.FarmerSeedDetailCreateView.as_view(), name="farmer_seed_details_create"),
    path('farmer/organic_crop/seed_details/<uuid:pk>/update/', views.FarmerSeedDetailUpdateView.as_view(), name="farmer_seed_details_update"),
    
    path('farmer/organic_crop/<uuid:pk>/nutrient_details/create/', views.FarmerNutrientDetailCreateView.as_view(), name="farmer_nutrient_details_create"),
    path('farmer/organic_crop/nutrient_details/<uuid:pk>/update/', views.FarmerNutrientDetailUpdateView.as_view(), name="farmer_nutrient_details_update"),
    
    path('farmer/organic_crop/<uuid:pk>/pest_disease_management/create/', views.FarmerPestDiseaseManagementCreateView.as_view(), name="farmer_pest_disease_management_create"),
    path('farmer/organic_crop/pest_disease_management/<uuid:pk>/update/', views.FarmerPestDiseaseManagementUpdateView.as_view(), name="farmer_pest_disease_management_update"),
    
    path('farmer/organic_crop/<uuid:pk>/weed_management/create/', views.FarmerWeedManagementCreateView.as_view(), name="farmer_weed_management_create"),
    path('farmer/organic_crop/weed_management/<uuid:pk>/update/', views.FarmerWeedManagementUpdateView.as_view(), name="farmer_weed_management_update"),
    
    path('farmer/organic_crop/<uuid:pk>/harvest_income/create/', views.FarmerHarvestIncomeCreateView.as_view(), name="farmer_harvest_income_create"),
    path('farmer/organic_crop/harvest_income/<uuid:pk>/update/', views.FarmerHarvestIncomeUpdateView.as_view(), name="farmer_harvest_income_update"),
    
    path('farmer/organic_crop/<uuid:pk>/cost_of_cultivation/create/', views.FarmerCostOfCultivationCreateView.as_view(), name="farmer_cost_of_cultivation_create"),
    path('farmer/organic_crop/cost_of_cultivation/<uuid:pk>/update/', views.FarmerCostOfCultivationUpdateView.as_view(), name="farmer_cost_of_cultivation_update"),
    
    path('farmer/organic_crop/<uuid:pk>/contamination_control/create/', views.FarmerContaminationControlCreateView.as_view(), name="farmer_contamination_control_create"),
    path('farmer/organic_crop/contamination_control/<uuid:pk>/update/', views.FarmerContaminationControlUpdateView.as_view(), name="farmer_contamination_control_update"),
    
    path('farmer/<uuid:farmer_pk>/organic_crop/generate_pdf/', views.GenerateOrganicCropPdfView.as_view(), name="generate_organic_crop_pdf"),
    
    path('vendor/list/', views.VendorListView.as_view(), name="vendor_list"),
    path('vendor/create/', views.VendorCreateView.as_view(), name="vendor_create"),
    path('vendor/<uuid:pk>/update/', views.VendorUpdateView.as_view(), name="vendor_update"),
    
    
    
    path('season/list/', views.SeasonListView.as_view(), name="season_list"),
    path('season/create/', views.SeasonCreateView.as_view(), name="season_create"),
    path('season/<uuid:pk>/update/', views.SeasonUpdateView.as_view(), name="season_update"),
    

    path('costs/list/', views.CostsListView.as_view(), name="costs_list"),
    path('costs/create/', views.CostsCreateView.as_view(), name="costs_create"),
    path('costs/<uuid:pk>/update/', views.CostsUpdateView.as_view(), name="costs_update"),
    
    
    path('dashboard/farmer/', views.DashboardFarmerView.as_view(), name="dashboard_farmer_view"),
    path('farmer/list/download/', views.FarmerCSV.as_view(), name='farmer_download_csv'),
    path('other_farmer/list/download/', views.OtherFarmerCSV.as_view(), name='other_farmer_download_csv'),
    path('organic_crop/csv/', views.OrganicCropCsv.as_view(), name="organic_crop_download_csv"),
    path('vendor/download/', views.VendorCSV.as_view(), name="vendor_download_csv"),
    
    path('traceability/ginning_mapping/create/', views.GinningMappingCreateWizardView.as_view(), name="traceability_ginning_mapping_create"),
    path('traceability/get_ginnings/', views.GetGinningList.as_view(), name="get_ginnings"),
    path('traceability/ginning/list/', views.GinningListView.as_view(), name="ginning_list_view"),
    path('traceability/ginning/<uuid:pk>/qc_request/', views.GinningQcRequestCreateView.as_view(), name="ginning_qc_request_create_view"),
    path('traceability/ginning/<uuid:pk>/create/inbound_request/', views.GinningInboundRequest.as_view(), name="ginning_inbound_request_create_view"),
    
    path('traceability/spinning_mapping/create/', views.SpinningMappingCreateWizardView.as_view(), name="traceability_spinning_mapping_create"),
    path('traceability/get_spinnings/', views.GetSpinningList.as_view(), name="get_spinnings"),
    path('traceability/spinning/list/', views.SpinningListView.as_view(), name="spinning_list_view"),
    path('traceability/spinning/<uuid:pk>/qc_request/', views.SpinningQcRequestCreateView.as_view(), name="spinning_qc_request_create_view"),
    path('traceability/spinning/<uuid:pk>/create/inbound_request/', views.SpinningInboundRequest.as_view(), name="spinning_inbound_request_create_view"),
    
    
]
