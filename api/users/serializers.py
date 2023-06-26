from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD
    default_error_messages = {
        'no_active_account': _('The email address or password entered is incorrect'),
        'email_not_verified': _('The email address has not been verified'),
    }


class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        # if not self.user:
        #     raise exceptions.AuthenticationFailed(
        #         self.error_messages['email_not_verified'],
        #         'email_not_verified',
        # )
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        # data['account_id'] = str(self.user.id)
        return data
