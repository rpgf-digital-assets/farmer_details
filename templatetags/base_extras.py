from django import template
from django.db.models import ForeignKey
register = template.Library()

@register.simple_tag
def model_to_dict(instance):
    data = {}
    for field in instance._meta.get_fields():
        data[field.verbose_name] = field.value_from_object(instance)
    return data