
import logging
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm,
    _unicode_ci_compare
)
from django.contrib.auth.password_validation import validate_password
from django.forms import (
    CharField,
    EmailField,
    EmailInput,
    FileInput,
    Form,
    ImageField,
    PasswordInput,
    Select,
    TextInput,
    ValidationError,
)
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from users.models import User
from .utils import input_is_all_digits
from .validators import validate_phonenumber
from django.contrib.auth.password_validation import password_validators_help_texts

logger = logging.getLogger(__name__)



class IndividualSignUpFirstPageForm(Form):
    """
    Form used in `Individual SignUp` first page.
    It is the first step of the form wizard. 
    """
    email = EmailField(label='Email id', widget=EmailInput(attrs={'class': 'form-control form-control-lg',
                                                                                  'placeholder': 'Email',
                                                                                  }))
    password = CharField(label='Password', 
                         widget=PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Password'}),
                         help_text = password_validators_help_texts
                        )
    confirm_password = CharField(label='Confirm Password', widget=PasswordInput(attrs={'class': 'form-control form-control-lg',
                                                                                                       'placeholder': 'Confirm Password'}))
    phone = CharField(label='Phone no.', validators=[validate_phonenumber],
                      widget=TextInput(attrs={'class': 'form-control form-control-lg',
                                                       'placeholder': 'Phone',
                                              }))
    
    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            raise ValidationError(
                f'User with this email address({email}) already exists')
        return email.lower()

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        user = User.objects.filter(phone=phone).first()
        if user:
            raise ValidationError(
                f'User with this phone({phone}) already exists')
        return phone

    def clean(self):
        form_data = self.cleaned_data
        password = form_data.get("password")
        confirm_password = form_data.get("confirm_password")

        # validate password
        try:
            validate_password(password)
        except ValidationError as error:
            error_string = '<ul>'
            for err in error:
                error_string += f"<li>{err} </li>"

            error_string += '</ul>'
            self._errors["password"] = error_string

        if password != confirm_password:
            self._errors["password"] = "Password and Confirm Password does not match"
            self._errors["confirm_password"] = "Password and Confirm Password does not match"

        for field in form_data:
            if field != "address" and field != "profile_image":
                if form_data[field] == '' or form_data[field] == ' ' or form_data[field] is None:
                    # Will raise a error message
                    self._errors[field] = "This field is required."
        return form_data





class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom Password Reset Form
    Field properties changed
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Email Address"
        self.fields['email'].widget.attrs['class'] = 'form-control form-control-solid h-auto py-6 px-6 rounded-lg font-size-h6'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'

    def get_users(self, email):
        """Given an email an an unusable password, 
        return matching user(s) who should receive a set password link.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users from
        resetting their password.
        """
        email_field_name = User.get_email_field_name()
        active_users = User._default_manager.filter(**{
            '%s__iexact' % email_field_name: email,
            'is_active': True,
        })
        return (
            u for u in active_users
            if _unicode_ci_compare(email, getattr(u, email_field_name))
        )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom Password Set Form
    Field properties changed
    """
    new_password1 = CharField(help_text = password_validators_help_texts, widget=PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = "New Password"
        self.fields['new_password2'].label = "Confirm New Password"
        self.fields['new_password1'].widget.attrs['placeholder'] = _(
            "New Password")
        self.fields['new_password2'].widget.attrs['placeholder'] = _(
            "Confirm New Password")
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-solid h-auto py-6 px-6 rounded-lg font-size-h6'

class CustomSetPasswordByAdminForm(CustomSetPasswordForm):
    """
    Custom Password Set Form to be used by admin 
    Field properties changed
    init does not required user object
    """
    
    def __init__(self, *args, **kwargs):
        # do not need user for initialization
        Form.__init__(self, *args, **kwargs)
        self.fields['new_password1'].label = "New Password"
        self.fields['new_password2'].label = "Confirm New Password"
        self.fields['new_password1'].widget.attrs['placeholder'] = _(
            "New Password")
        self.fields['new_password2'].widget.attrs['placeholder'] = _(
            "Confirm New Password")
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-solid h-10 py-6 px-6 rounded-lg font-size-h6 pr-12'

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        validate_password(password2)
        return password2
        
    def save(self, commit=True):
        return True


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom Password Change Form
    Field properties changed
    """
    new_password1 = CharField(help_text = password_validators_help_texts, widget=PasswordInput())
    
    error_messages = {
        **PasswordChangeForm.error_messages,
        'old_and_new_passwords_match': _("Old password and new password cannot be same."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = "Old Password"
        self.fields['new_password1'].label = "New Password"
        self.fields['new_password2'].label = "Confirm New Password"
        self.fields['old_password'].widget.attrs['placeholder'] = _(
            "Old Password")
        self.fields['new_password1'].widget.attrs['placeholder'] = _(
            "New Password")
        self.fields['new_password2'].widget.attrs['placeholder'] = _(
            "Confirm New Password")
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-solid h-auto py-6 px-6 rounded-lg font-size-h6 pr-12'
            
    def clean(self):
        """
        Validate that the new_password1 field is correct.
        """
        new_password1 = self.cleaned_data.get("new_password1")
        old_password = self.cleaned_data.get("old_password")
        if new_password1 == old_password:
            self._errors["new_password1"] = self.error_messages['old_and_new_passwords_match']
        super(CustomPasswordChangeForm, self).clean()

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.force_change_password = False
        if commit:
            self.user.save()
        return self.user
    
class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom Login Form for Impava Site Admins
    Takes EmailOrPhone instead of username
    """
    email = EmailField(
        label="Email Address",
        widget=EmailInput(
            attrs={
                'placeholder': _('Email Address')
            }
        )
    )
    message_incorrect_password = _(
        'The email address or password entered is incorrect')
    message_inactive = _(
        'The email address or phone number associated with this account is unverified')

    class Meta:
        model = User
        fields = ["email", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['username']
        self.fields['password'].label = _("Password")
        self.fields['password'].widget.attrs['placeholder'] = _('Password')
        self.order_fields(['email', 'password'])
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-solid h-auto py-6 px-6 rounded-lg font-size-h6'

    def clean_email(self):
        email = self.cleaned_data['email']
        return User.objects.normalize_email(email)
        

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(
                email=email, password=password)
            if self.user_cache is None:
                logger.warning(f'users-forms-CustomAuthenticationForm: Incorrect password for email {email}')
                raise ValidationError(self.message_incorrect_password)
            # if not (self.user_cache.email_verified and self.user_cache.phone_verified):
            #     logger.warning(f'users-forms-CustomAuthenticationForm: User not verified, "email_verified": {self.user_cache.email_verified}, "phone_verified": {self.user_cache.phone_verified}')
            #     url = reverse('users:resend_email_verification_link',
            #                   kwargs={'user_id': self.user_cache.id})
            #     self._errors[
            #         "email"] = f"<li>Your email is not verified, Click <a id='email-verification-link' href='{url}'>'here'</a> to get the email verification link</li> "

                # raise ValidationError(self.message_inactive)
        return cleaned_data


    
