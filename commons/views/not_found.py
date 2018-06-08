import time
from uuid import uuid4

from django.urls import resolve

from commons.utils.http_error import NotFound
from commons.utils.loggers import log_request, log_response


def http_not_found_view(request, *args, **kwargs):
    '''View handler for http 404 not found
    '''
    request_id = str(uuid4())
    request_epoch = time.time()*1000

    log_request(request_id, request, request_epoch)

    response = NotFound().response

    log_response(request_id, request, request_epoch, response)

    return response
