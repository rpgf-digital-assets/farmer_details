from functools import wraps

from django.urls.base import resolve
from django.core.exceptions import PermissionDenied
import requests
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def logout_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME,
                    logout_url=settings.LOGOUT_URL):
    """
    Decorator for views that checks that the user is logged OUT, redirecting
    to the log-out page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=logout_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator