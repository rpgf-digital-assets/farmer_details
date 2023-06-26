from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import resolve, reverse
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
from utils.helpers import get_or_none


def enforce_csrf(request):
    check = CSRFCheck()
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)


def check_custom_header(request):
    account_id = request.META.get(settings.HEADER_ACCOUNT_ID, 'null')
    if account_id == 'null':
        raise AuthenticationFailed(
            detail='account-id header missing.', code='header_missing')
    return account_id


class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        # check_custom_header(request)

        if header is None:
            raw_token = request.COOKIES.get(
                settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        # enforce_csrf(request)

        return self.get_user(validated_token), validated_token


class AuthenticationForPasswordChange(JWTAuthentication):
    def authenticate(self, request):
        if request.path == '/api/accounts/reset_user_password/':
            if request.data['account_authentication'] != settings.ACCOUNT_VERIFICATION:
                raise AuthenticationFailed(
                    detail='Account Verification failed', code='data_missing')
            user = get_or_none(User, phone=request.data['phone_number'])
            return user, None
        else:
            header = self.get_header(request)
            check_custom_header(request)

            if header is None:
                raw_token = request.COOKIES.get(
                    settings.SIMPLE_JWT['AUTH_COOKIE']) or None
            else:
                raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None

            validated_token = self.get_validated_token(raw_token)
            enforce_csrf(request)

            return self.get_user(validated_token), validated_token
