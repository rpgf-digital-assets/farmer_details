import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from env import *

DEBUG = True


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': f"{BASE_DIR}/db.sqlite3",
#         'OPTIONS': {
#             'timeout': 209,
#         }
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'farmer_prod',
        'USER': 'farmer',
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': 'LOCALHOST'
    }
}

######################### MEDIA CONFIGURATION #################

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


