import json
from django import template
from django.db.models import ForeignKey
from django.urls import reverse
register = template.Library()

@register.simple_tag
def model_to_dict(instance, extra_fields=None):
    data = {}
    for field in instance._meta.get_fields():
        try:
            data[field.verbose_name] = field.value_from_object(instance)
        except: 
            pass
    if extra_fields:
        extra_fields_dict = json.loads(extra_fields)
        for field_name, field_verbose_name in extra_fields_dict.items():
            data[field_verbose_name] = getattr(instance, field_name)
    return data



@register.simple_tag
def navactive(request, url, *args, **kwargs):
    """
    Checks if the navbar element corresponds to the current url or not
    params: request - request
            url - url name
            args - add url params ONLY
            kwargs - get_vars: exact get vars string eg 'var1=test&var2=123'
    """
    check_url = reverse(url, args=args)
    get_confirmed = True
    get_vars = kwargs.get('get_vars')
    if get_vars:
        get_vars_list = get_vars.split('&')
        for get_var in get_vars_list:
            k, v = get_var.split('=')
            if request.GET.get(k) != v:
                get_confirmed = False
    if request.path == check_url and get_confirmed:
        return 'active'
    return ""

@register.filter
def is_list(value):
    return isinstance(value, list)


from django.utils.safestring import mark_safe

@register.simple_tag
def add_items_to_dict(dict_1, dict_2):
    print("🐍 File: templatetags/base_extras.py | Line: 50 | undefined ~ dict_2",dict_2)
    res = json.loads(dict_2)
    print("🐍 File: templatetags/base_extras.py | Line: 46 | undefined ~ dict_2", res, type(res))
    result = {**dict_1, **res}
    print("🐍 File: templatetags/base_extras.py | Line: 55 | add_items_to_dict ~ result",result, type(result))
    return result