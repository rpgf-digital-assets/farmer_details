import os
from env import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('FARMER_DATABASE_NAME'),
#         'USER': os.environ.get('FARMER_DATABASE_USER'),
#         'PASSWORD': os.environ.get('FARMER_DATABASE_PASSWORD'),
#         'HOST': os.environ.get('FARMER_DATABASE_HOST'),
#         'PORT': '5432',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': f"{BASE_DIR}/db.sqlite3",
    }
}


STORAGES = {"default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}}


AWS_S3_CUSTOM_DOMAIN = "farm-portal.s3.amazonaws.com"
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'farmer_details.storage_backends.MediaStorage'
