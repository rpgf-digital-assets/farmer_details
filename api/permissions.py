from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from users.models import User


    
class IsAdminOrSuperUser(BasePermission):
    """
    Allows access only to Admin.
    """

    def has_permission(self, request, view):
        print("🐍 File: api/permissions.py | Line: 16 | has_permission ~ request.user",request.user)
        user = get_object_or_404(User, id=request.user.id)
        return user.role == User.SUPER_USER or user.role == User.ADMIN
