import os 
from celery import Celery 
# Set default Django settings 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmer_details.settings')

app = Celery('farmer_details')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

