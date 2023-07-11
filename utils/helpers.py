import json
import uuid
from rest_framework.response import Response
from django.db import models
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Base model for storing historical records
    and uuid identifiers
    """
    class Meta:
        abstract = True
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(_('is Active?'), default=True, editable=False)
    history = HistoricalRecords(inherit=True)
    
    


def get_or_none_for_manager(manager, select_related=[], **kwargs):
    # common get or none logic extended by all
    # other get or none utils
    # using .last() instead of .first() because old logic used the same

    queryset = manager.filter(**kwargs)

    if select_related:
        queryset = queryset.select_related(*select_related)

    try:
        return queryset.last()
    except (
        manager.model.DoesNotExist,
        ValueError,
        TypeError,
        IndexError,
    ):
        return None


def get_or_none(model, select_related=[], **kwargs):
    return get_or_none_for_manager(model.objects, select_related=select_related, **kwargs)


def error_response(status, msg, data, *args, **kwargs):
    response = {
        "status_code": status,
        "status": "failure",
        "detail": msg,
        "data": data,
    }
    caller_func = kwargs.get("caller_func", None)
    return Response(data=response, status=status)


def success_response(status, msg, data, *args, **kwargs):
    response = {
        "status_code": status,
        "status": "success",
        "detail": msg,
        "data": data,
    }
    return Response(data=response, status=status)


def custom_response(status_code, custom_code, msg, display_msg, data, navigate='', valid=True, *args, **kwargs):

    response = {
        "status_code": status_code,
        "message": msg,
        "display_message": display_msg,
        "data": data,
        "navigate": navigate,
        "custom_code": custom_code,
        "valid": valid

    }

    return Response(data=response, status=status_code)


def build_request(request, ist, url, body):

    method = request.method
    custom_headers = json.dumps({
        "REQUEST_METHOD": request.META.get('REQUEST_METHOD'),
        "HTTP_REFERER": request.META.get('HTTP_REFERER', None),
        "HTTP_ACCOUNT_ID": request.META.get('HTTP_ACCOUNT_ID', None)
    })
    if(request.META.get('CONTENT_TYPE') == 'application/json'):
        if body == "":
            posted_body = str(body)
        else:
            posted_body = str(body)
    else:
        posted_body = "{}"
    log = "".join("===> "+str(ist)+" "+method+" "+url+"\n"+custom_headers +
                  "\n"+"posted_data : " + posted_body+"\n")
    return log


def check_url(request):
    url = request.build_absolute_uri()

    if '/api/' in url:
        return True, url
    else:
        return False, url
