from django.urls import path
from . import views

urlpatterns = [
    path('farmer/list/', views.FarmersListView.as_view(), name='farmers_list'),
    path('farmer/create/', views.FarmerCreateView.as_view(), name='farmer_create'),
    path('farmer/<uuid:pk>/update/', views.FarmerUpdateView.as_view(), name='farmer_update'),
    path('farmer/<uuid:pk>/overview/', views.FarmerDetailsView.as_view(), name='farmer_overview'),
    path('farmer/<uuid:pk>/social/create/', views.FarmerSocialCreateView.as_view(), name="farmer_social_create"),
    path('farmer/social/<uuid:pk>/update/', views.FarmerSocialUpdateView.as_view(), name="farmer_social_update"),
    path('farmer/<uuid:pk>/land_details/create/', views.FarmerLandDetailCreateView.as_view(), name="farmer_land_details_create"),
    path('farmer/land_details/<uuid:pk>/update/', views.FarmerLandDetailUpdateView.as_view(), name="farmer_land_details_update"),
    
    path('dashboard/farmer/', views.DashboardFarmerView.as_view(), name="dashboard_farmer_view"),
    
]
