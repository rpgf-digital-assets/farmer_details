from .models import User
from django.contrib.auth.backends import BaseBackend

class EmailAuthenticationBackend:
    """
    Custom Authentication Backend that authenticates based on email address
    """

    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            pwd_valid = user.check_password(password)
            if pwd_valid:
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class LinkedInAuthenticationBackend(BaseBackend):

    def authenticate(self, request, email=None):
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try: 
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None