import json
import re
from datetime import datetime

from jsonschema import Draft4Validator

from bson.objectid import ObjectId
from commons.utils.http_error import BadRequest
from django.urls import resolve

from .helpers import RequestValidationConfig


class RequestValidationMiddleware:
    '''Middleware for validating incoming request url param, query params, body according to request validation config.

    Attributes:
        get_response: handler method of next middleware or view
    '''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        '''Handler method for middleware

        Args:
            request: Django's request object.

        Returns:
            Response passed by next middleware or view.

        Raises:
            BadRequest: If request validation fails.

        '''
        request_parameters = resolve(request.path_info)
        request_info = {
            'route_name': request_parameters.url_name,
            'url_parameters': request_parameters.kwargs,
            'query_parameters': dict(request.GET),
            'request_body': request.body if request.body else {},
            'method': request.method
        }

        request_validator(request_info)

        response = self.get_response(request)

        return response


class ValidateParamType(object):
    '''Validate data type of a param given it's config.

    Attributes:
        __document: dictionary containing config to validate a param
        __value: value of the param
        __validation_types: dictionary containing validator method for each type
    '''

    def __init__(self, document, value):
        self.__document = document
        self.__value = value
        self.__validation_types = {
            'STRING': self.__validate_string_params,
            'INTEGER': self.__validate_integer_params,
            'OBJECT_ID': self.__validate_object_id_params,
            'FLOAT': self.__validate_float_params,
            'DATE': self.__validate_date_params
        }

    def validate(self):
        '''This method is used to validate param for string, integer, object_id or float data type.

        Returns:
            List of errors

            Example:
                [
                    {
                        "message": "id must be of interger type"
                    }
                ]
        '''

        if not self.__validation_types.get(self.__document.get('dataType')):
            return [{
                "message": self.__document.get('name') + " has unknown data type: " + self.__document.get('dataType')
            }]

        return self.__validation_types.get(self.__document.get('dataType'))()

    def __validate_integer_params(self):
        '''This method is used to validate param for integer data type.

        Returns:
            List of errors

            Example:
                [
                    {
                        "message": "id must be of interger type"
                    }
                ]
        '''

        errors = []

        if str(self.__value).isdigit():

            if self.__document.get('action'):
                action_errors = self.__validate_param_constraint(
                    self.__document, int(self.__value)
                )

                if action_errors:
                    errors += action_errors

        else:
            errors.append({
                "message": self.__document.get('name') + " must be of integer type"
            })

        return errors

    def __validate_float_params(self):
        '''This method is used to validate param for float data type.

        Returns:
            List of errors

            Example:
                [
                    {
                        "message": "id must be of float type"
                    }
                ]
        '''

        errors = []

        if re.match("^\d+?\.\d+?$", str(self.__value)) is None:
            error_obj = {
                "message": self.__document.get('name') + " must be of float type"
            }
            errors.append(error_obj)

        else:

            if self.__document.get('action'):
                action_errors = self.__validate_param_constraint(self.__document, float(self.__value))

                if action_errors:
                    errors += action_errors

        return errors

    def __validate_object_id_params(self):
        '''This method is used to validate wether the param value is a valid ObjectId.

        Returns:
            List of errors

            Example:
                [
                    {
                        "message": "id must be of type ObjectId"
                    }
                ]
        '''

        errors = []

        if ObjectId.is_valid(str(self.__value)):

            if self.__document.get('action'):
                action_errors = self.__validate_param_constraint(self.__document, self.__value)

                if action_errors:
                    errors += action_errors

        else:
            error_obj = {
                "message": self.__document.get('name') + " must be of type ObjectId"
            }
            errors.append(error_obj)

        return errors

    def __validate_string_params(self):
        '''This method is used to validate wether the param value is a valid string.

        Returns:
            List of errors

            Example:
                [
                    {
                        "message": "id must follow regex",
                        "regex": "^\d+?\.\d+?$"
                    }
                ]
        '''

        errors = []

        if isinstance(self.__value, str):

            if self.__document.get('regex') and re.match(self.__document.get('regex'), self.__value) is None:
                error_obj = {
                    "message": self.__document.get('name') + " must follow regex " + self.__document.get('regex')
                }
                errors.append(error_obj)

            else:

                if self.__document.get('action'):
                    action_errors = self.__validate_param_constraint(self.__document, self.__value)

                    if action_errors:
                        errors += action_errors
        else:
            errors.append({
                "message": self.__document.get('name') + " must be of string type"
            })

        return errors

    def __validate_date_params(self):
        '''This method is used to validate wether the param value is a valid date.

        Returns:
            List of errors

            Example:
                [
                    {
                        "message": "from must be of date type with format %Y-%m-%d"
                    }
                ]
        '''

        errors = []

        try:
            date = datetime.strptime(str(self.__value), str(self.__document.get('format')))

        except ValueError:
            errors.append({
                "message": (self.__document.get('name') + " must be of date type with format " +
                            self.__document.get('format'))
            })

            return errors

        if self.__document.get('action'):
            action_errors = self.__validate_param_constraint(self.__document, date)

            if action_errors:
                errors += action_errors

        return errors

    def __validate_param_constraint(self, param_info, param_value):
        '''This method is used to check various types of constraints on param.

        Args:
            param_info (Object): Contains query or url param info
            param_value: Value of the param obtained from request.

        Returns:
            List of errors against each type of query param

            Example:
                [
                    {
                        "message": "strategyId out of range",
                        "expectedRange": {
                            "min": 100,
                            "max": 200
                        }
                    },
                    {
                        "message": "id incorrect value",
                        "expectedValue": 12
                    }
                ]
        '''

        error = []
        action_type = self.__document['action'].get('actionType')
        values = self.__document['action'].get('value')

        if action_type == 'BETWEEN':

            if not(param_value >= values.get('min') and param_value <= values.get('max')):
                error.append({
                    "message": param_info.get('name') + " out of range",
                    "expectedRange": {
                        "min": str(values.get('min')),
                        "max": str(values.get('max'))
                    }
                })

        elif action_type == 'EQUALS':

            if param_value != values:
                error.append({
                    "message": param_info.get('name') + " incorrect value",
                    "expectedValue": values
                })

        elif action_type == 'IN':

            if param_value not in values:
                error.append({
                    "message": param_info.get('name') + " incorrect value",
                    "expectedValues": values
                })

        elif action_type == 'GREATER_THAN':
            if param_value <= values:
                error.append({
                    "message": param_info.get('name') + " should be greater than" + values,
                })
        elif action_type == 'LESS_THAN':
            if param_value >= values:
                error.append({
                    "message": param_info.get('name') + " should be less than" + values,
                })

        return error


def validate_params(param_schema, request_info, param_type):
    '''Validate url and query params of a request.

    Args:
        param_schema: list of dictionaries containing param configs.
        request: Django request object.
        param_type: It can be urlParams or queryParams
    '''

    response = []

    for doc in param_schema:
        value = None

        if param_type == "urlParams":
            value = request_info['url_parameters'].get(str(doc.get('name')))

        elif param_type == "queryParams":
            value = request_info['query_parameters'].get(str(doc.get('name')), [''])[0]

        if not value and doc.get('isRequired'):
            response.append({
                "message": doc.get('name') + " param is manadatory",
                "type": doc.get('dataType')
            })

        if value:
            validation_status = ValidateParamType(doc, value).validate()

            if validation_status:
                response += validation_status

    return response if response else None


def validate_json_body(body, schema):
    '''This method is used to validate request body against defined schema.

    Args:
        body: JSON like dictionary request body
        schema: JSON like dictionary schema for sent request body

    Returns:
        List of errors against each key in json request body

        Example:
            [
                {
                    3 is not of type 'string',
                    {} is not of type 'string'
                }
            ]
    '''

    errors = []
    validator = Draft4Validator(schema)

    for error in sorted(validator.iter_errors(body)):
        errors.append(error.message)

    return errors if errors else None


def request_validator(request_info):

    '''This method is used to validate all incoming requests before the request goes to handlers.
        It validates url params, query params and request body for expected schema.

    Args:
        request_info: Dictonary containing information extracted from Django's request object.

    Returns:
        True: If request validates according to route config.

    Raises:
        BadRequest: In case any of the query param does not match with the expected value

        Example:
            {
                "error": {
                    "message": "Request validation failed",
                    "code": 400,
                    "errors": {
                        "urlParams": [
                            {
                                "message": "healthModuleId must be of integer type"
                            }
                        ]
                    }
                }
            }

    '''

    config_query = {
        'routeName': request_info['route_name'],
        'isActive': True,
        'method': request_info['method']
    }

    request_config = RequestValidationConfig.objects.get_one(queries=config_query)

    if request_config:
        response = {}
        query_param_schema = request_config.get('queryParams')
        url_param_schema = request_config.get('urlParams')
        request_body_schema = request_config.get('requestBodySchema')

        if query_param_schema:
            query_param_status = validate_params(query_param_schema, request_info, 'queryParams')
            if query_param_status:
                response["queryParams"] = query_param_status

        if url_param_schema:
            url_param_status = validate_params(url_param_schema, request_info, 'urlParams')
            if url_param_status:
                response["urlParams"] = url_param_status

        if request_body_schema:
            request_body_status = None

            try:
                data = json.loads(request_info['request_body'].decode('utf-8'))
            except Exception:
                request_body_status = [{"message": "Invalid request body."}]

            else:
                request_body_status = validate_json_body(data, request_body_schema)

            if request_body_status:
                response["requestBody"] = request_body_status

        if response:
            raise BadRequest(errors=response)

    return True
