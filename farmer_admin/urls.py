from django.urls import path
from . import views

urlpatterns = [
    path('farmer/list/', views.FarmersListView.as_view(), name='farmers_list'),
    path('farmer/create/', views.FarmerCreateView.as_view(), name='farmer_create'),
    path('farmer/<uuid:pk>/update/', views.FarmerUpdateView.as_view(), name='farmer_update'),
]
