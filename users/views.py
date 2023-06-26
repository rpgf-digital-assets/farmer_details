from django.shortcuts import render
from django.views.generic import (
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View
)
from django.contrib.auth import logout

from users.forms import CustomAuthenticationForm
from .decorators import logout_required
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator


# Create your views here.

    
@method_decorator([logout_required], name="dispatch")
class CustomLoginView(LoginView):
    """
    This view handles the Login
    """
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm
    
    def get_success_url(self):
        return super().get_success_url()
    
    
    def form_valid(self, form):
        return super().form_valid(form)



class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        data = super().dispatch(request, *args, **kwargs)
        return data


