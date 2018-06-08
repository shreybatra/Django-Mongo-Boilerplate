import traceback
from uuid import uuid4

from commons.utils.http_error import (HttpError, InternalServerError,
                                      MethodNotAllowed)
from commons.utils.loggers import error_logger
from django.conf import settings
from django.http.response import (HttpResponse, HttpResponseNotAllowed,
                                  JsonResponse, StreamingHttpResponse)


class HandleExceptionMiddleware:
    '''Middleware for handling exceptions.

    Attributes:
        get_response: handler method of next middleware or view
    '''

    def __init__(self, get_response):
        self.get_response = get_response

        # overriding Django's inbuilt error handling
        setattr(settings, 'DEBUG_PROPAGATE_EXCEPTIONS', True)

    def __call__(self, request):
        '''Handler method for middleware

        Args:
            request: Django's request object.

        Returns:
            Response passed by next middleware or view.

        '''

        try:
            response = self.get_response(request)

            if isinstance(response, HttpResponseNotAllowed):
                raise MethodNotAllowed

            if isinstance(response, (HttpResponse, StreamingHttpResponse)):
                return response
            else:
                return JsonResponse(response)

        except HttpError as e:
            return e.response

        except Exception as e:
            request_id = str(uuid4())
            setattr(request, 'request_id', request_id)
            # log unhandled exception
            error = traceback.format_exc()
            log = '{uuid} :: \n{traceback}\n\n---------------------------------------------------------'.format(
                uuid=request.request_id,
                traceback=error
            )
            error_logger.error(log)
            traceback.print_exc()

            # send default error response hiding sensitive exception details
            return InternalServerError().response
