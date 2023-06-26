from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('accounts/', include(('api.users.urls', 'api_users'), namespace="api_users")),
    path('farmer_admin/', include(('api.farmer_admin.urls', 'api_farmer_admin'), namespace="api_farmer_admin")),
]
