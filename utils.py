import uuid
from django.db import models
from simple_history.models import HistoricalRecords


class BaseModel(models.Model):
    """Base model for storing historical records
    and uuid identifiers
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    history = HistoricalRecords()
    
