import re
import phonenumbers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_phonenumber(phone):
    """
    Validate if input is a phone number
    """
    try:
        formatted_phone = phonenumbers.parse(phone)
        assert phonenumbers.is_valid_number(formatted_phone)
    except (phonenumbers.NumberParseException, AssertionError):
        raise ValidationError(
            'Enter a valid phone number (e.g. +12125552368).')

def validate_name(name):
    if name.isnumeric():
        raise(ValidationError('Enter a valid name.'))
    

def validate_positive_number(number):
    if number < 1:
        raise ValidationError(
            'Number should not be less than 1.')


class NumberValidator(object):
    """
    Custom Password Validator: Checks if password contains atleast 1 Digit
    """
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("The password must contain at least 1 digit, 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 digit, 0-9."
        )


class UppercaseValidator(object):
    """
    Custom Password Validator: Checks if password contains atleast 1 Uppercase Character
    """
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase letter, A-Z."
        )


class LowercaseValidator(object):
    """
    Custom Password Validator: Checks if password contains atleast 1 Lowercase Character
    """
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter, a-z."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 lowercase letter, a-z."
        )


class SymbolValidator(object):
    """
    Custom Password Validator: Checks if password contains atleast 1 Symbol
    """
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                _("The password must contain at least 1 symbol: " +
                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 symbol: " +
            "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
        )
