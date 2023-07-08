from django.contrib import messages
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from users.models import User


class AdminRequiredMixin:
    """
     This Mixin is used to check if the logged in user is a `Admin`
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == User.SUPER_USER or request.user.role == User.ADMIN:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, _('Access Denied: Admin role Required'))
        logout(request)
        raise PermissionDenied