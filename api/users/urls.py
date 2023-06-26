from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'api_users'

urlpatterns = [
    # path('individual_details/', views.IndividualDetailsAPIView.as_view(),
    #      name="individual_details_api_view"),
    # path('individual_signup/first_page/', views.IndividualSignupFirstPageAPIView.as_view(),
    #      name="individual_signup_first_page_api_view"),
    # path('individual_signup/', views.IndividualSignupAPIView.as_view(),
    #      name="individual_signup_api_view"),
    path('login/', views.LoginAPIView.as_view(),
        name="login_api_view"),
    path('refresh_token/', TokenRefreshView.as_view(),
        name='refresh_token_api_view'),
]