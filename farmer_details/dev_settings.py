import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': f"{BASE_DIR}/db.sqlite3",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'nutrify_uat',
#         'USER': 'nutrify',
#         'PASSWORD': 'nutrify321',
#         'HOST': 'nutrifydb.cnx3p6vrw0qk.ap-south-1.rds.amazonaws.com',
#         'PORT': '5432',
#     }
# }

######################### MEDIA CONFIGURATION #################

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


