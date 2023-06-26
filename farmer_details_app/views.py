from django.shortcuts import redirect, render
from django.views.generic import (
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View
)

from users.models import User

# Create your views here.

class IndexView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('users:login')
        return super().dispatch(request, *args, **kwargs)
    
    
    def get_template_names(self):
        if self.request.user.is_authenticated:
            if self.request.user.role == User.SUPER_USER:
                return 'farmer_admin/base.html'
            if self.request.user.role == User.ADMIN:
                return 'farmer_admin/base.html'
            if self.request.user.role == User.FARMER:
                return 'farmer_admin/base.html'
