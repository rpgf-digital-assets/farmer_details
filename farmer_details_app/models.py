import uuid
from django.db import models
from simple_history.models import HistoricalRecords

# Create your models here.

class BaseModel(models.Model):
    """Base model for storing historical records
    and uuid identifiers
    """
    class Meta:
        abstract = True
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    history = HistoricalRecords(inherit=True)
    