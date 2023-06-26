"""
URL configuration for farmer_details project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('farmer_details_app.urls', 'farmer_details_app'), namespace="farmer_details_app"), name="farmer_details_app"),
    path('api/', include(('api.urls', 'api'), namespace="api"), name="api"),
    path('farmer_admin/', include(('farmer_admin.urls', 'farmer_admin'), namespace="farmer_admin"), name="farmer_admin"),
    path('account/', include(('users.urls', 'users'), namespace="users"), name="users"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
