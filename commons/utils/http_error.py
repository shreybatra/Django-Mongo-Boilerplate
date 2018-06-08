from django.http import JsonResponse


class HttpError(Exception):
    '''Http Error Exception to be extended for various Http error status codes

    Attributes:
        errors: errors dictionary (optional) revealing more details to be sent in response
        response: response body to be sent
    '''
    def __init__(self, status_code, message="", error_code=None, errors={}):
        response = {
          "statusCode": status_code,
          "error": {
            "message": message
          }
        }
        if error_code is not None:
            response['error']['code'] = error_code

        if errors is not None:
            response['error']['errors'] = errors

        setattr(self, 'errors', errors)
        setattr(self, 'response', JsonResponse(response, status=status_code))

        super(HttpError, self).__init__(self, message)


class BadRequest(HttpError):
    '''Exception for HTTP 400 extended from HttpError

    The server cannot or will not process the request due to an apparent client error.
    '''

    status_code = 400

    def __init__(self, message="The request is invalid. Please try again.", error_code=None, errors=None):
        super(BadRequest, self).__init__(self.status_code, message, error_code, errors)


class Unauthorized(HttpError):
    '''Exception for HTTP 401 extended from HttpError

    Use when authentication is required and has failed or has not yet been provided.
    Basically when access to resource needs login
    '''

    status_code = 401

    def __init__(self, message="Sent request is unauthorized. Please log in first.", error_code=None, errors=None):
        super(Unauthorized, self).__init__(self.status_code, message, error_code, errors)


class PaymentRequired(HttpError):
    '''Exception for HTTP 402 extended from HttpError

    The server cannot or will not process the request due to an apparent client error.
    '''

    status_code = 402

    def __init__(
        self, message="Please confirm your purchase first. Payment is required to access this resource",
        error_code=None, errors=None
    ):
        super(PaymentRequired, self).__init__(self.status_code, message, error_code, errors)


class Forbidden(HttpError):
    '''Exception for HTTP 403 extended from HttpError

    The user might be logged in but does not have the necessary permissions for the resource.
    '''

    status_code = 403

    def __init__(self, message="You don't have necessary permissions to access this resource.", error_code=None, errors=None):
        super(Forbidden, self).__init__(self.status_code, message, error_code, errors)


class NotFound(HttpError):
    '''Exception for HTTP 404 extended from HttpError

    The requested resource could not be found but may be available in future.
    '''

    status_code = 404

    def __init__(self, message="The resource you are looking for does not exist.", error_code=None, errors=None):
        super(NotFound, self).__init__(self.status_code, message, error_code, errors)


class MethodNotAllowed(HttpError):
    '''Exception for HTTP 405 extended from HttpError

    A request method is not supported for the requested resource.
    '''

    status_code = 405

    def __init__(self, message="This method is not allowed for the sent request.", error_code=None, errors=None):
        super(MethodNotAllowed, self).__init__(self.status_code, message, error_code, errors)


class Conflict(HttpError):
    '''Exception for HTTP 409 extended from HttpError

    Indicates that the request could not be processed because of conflict in the request.
    '''

    status_code = 409

    def __init__(self, message="The request seems to be conflicting.", error_code=None, errors=None):
        super(Conflict, self).__init__(self.status_code, message, error_code, errors)


class UnsupportedMediaType(HttpError):
    '''Exception for HTTP 415 extended from HttpError

    Indicates that the request could not be processed because of conflict in the request.
    Generally used for invalid file types during uploads.
    '''

    status_code = 415

    def __init__(self, message="The sent filetype(s) not supported.", error_code=None, errors=None):
        super(UnsupportedMediaType, self).__init__(self.status_code, message, error_code, errors)


class Locked(HttpError):
    '''Exception for HTTP 423 extended from HttpError

    The resource that is being accessed is locked.
    '''

    status_code = 423

    def __init__(self, message="This resource is currently locked! Please try again later.", error_code=None, errors=None):
        super(Locked, self).__init__(self.status_code, message, error_code, errors)


class InternalServerError(HttpError):
    '''Exception for HTTP 500 extended from HttpError

    A generic error message, error_code=None, given when an unexpected condition was encountered and no more specific
    message is suitable.
    '''

    status_code = 500

    def __init__(
        self, message="Looks like something went wrong! Please try again.\nIf the issue persists please contact support.",
        error_code=None, errors=None
    ):
        super(InternalServerError, self).__init__(self.status_code, message, error_code, errors)


class NotImplemented(HttpError):
    '''Exception for HTTP 501 extended from HttpError

    The server either does not recognize the request method, or it lacks the ability to fulfill the request.
    Usually this implies future availability
    '''

    status_code = 501

    def __init__(self, message="This action for sent request is yet to be implemented.", error_code=None, errors=None):
        super(NotImplemented, self).__init__(self.status_code, message, error_code, errors)
