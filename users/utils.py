import logging
import random
import string

# import boto3
import requests
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

    
DEFAULT_RANDOM_STRING_LENGTH = 8
logger = logging.getLogger('send_sms_logger')


def get_random_alphanumeric_string(string_length=DEFAULT_RANDOM_STRING_LENGTH,
                                   lowercase=True,
                                   uppercase=True,
                                   digits=True):
    """
    Create random alphanumeric string of given length and characterset
    """
    scope = ''
    if lowercase:
        scope += string.ascii_lowercase
    if uppercase:
        scope += string.ascii_uppercase
    if digits:
        scope += string.digits
    return ''.join(random.choice(scope) for _ in range(string_length))

def get_username(user):
    """
    Create random username for given user based on their name
    """
    if user.last_name:
        username = f'{user.first_name}_{user.last_name}_{get_random_alphanumeric_string()}'
    elif user.first_name:
        username = f'{user.first_name}_{get_random_alphanumeric_string()}'
    else:
        username = f'user_{get_random_alphanumeric_string()}'
    username = username.replace(' ', '_')
    from .models import User
    existing_user = User.objects.filter(username=username).first()
    if existing_user:
        return get_username(user)
    return username

def name_to_first_name_and_last_name(name):
    """
    Splits a single string of name into first and last name
    """
    name_list = name.split()
    first_name = name_list[0]
    last_name = ''
    if len(name) > 1:
        last_name = ' '.join(name_list[1:])
    return (first_name, last_name)


# def send_sms(to_phone_number, body_content):
#     """
#     Sends SMS using AWS SNS service
#     """
#     if settings.LOG_SMS:
#         logger.info(f'Message to {to_phone_number}: {body_content}')
#         return
    
#     custom_config = Config(
#         region_name=settings.AWS_REGION,
#         signature_version='v4',
#         retries={
#             'max_attempts': 10,
#             'mode': 'standard'
#         }
#     )
#     client = boto3.client(
#         'sns',
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#         config=custom_config
#     )
#     response = client.publish(
#         PhoneNumber=to_phone_number,
#         Message=f'{body_content}'
#     )

#     logger.info(f'Send Sms Response for number {to_phone_number}: {response}')
#     logger.info(f'Message= {body_content}')

# def send_otp(name, otp, to_phone_number):
#     """
#     Generate OTP and send it using send_sms
#     """
#     message_body_content = (
#         f'Your OTP to login at Nutrify Today for user {name} is {otp}.\n'
#         f'It is valid for {settings.TOTP_OTP_VALIDITY // 60} minutes.'
#     )
#     send_sms(to_phone_number, message_body_content)


def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    
    if content_type:
        if 'text' in content_type.lower():
            return False
        if 'html' in content_type.lower():
            return False
    return True

def update_profile_picture(individual_object, linkedin_profile_picture):

    image_file = ContentFile(linkedin_profile_picture.content, name=f'{individual_object.pk}_profile_image.png')
    individual_object.profile_image = image_file
    individual_object.save()

    return True


def get_expiry_date():
    return timezone.now() + timezone.timedelta(days=60)

    
def input_is_all_digits(input):
    if input.isdigit():
        raise ValidationError(_("Only digits are not allowed"), code="input_all_digit")
    
