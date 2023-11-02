
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class CustomLoginRequiredMixin(LoginRequiredMixin):
    """ 
     If the user is not logged in they are redirected to Index page
    """
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, _('Access Denied: Login Required'))
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
    def get_login_url(self):
        return f"{reverse('users:login')}?next={self.request.get_full_path()}"