"""
local exceptions
"""

from requests.models import Response


# ================================================================================================
class RestClientException(Exception):
    """wrapper exception"""

    pass


class RestClientResourceError(RestClientException):
    """wrapper exception"""

    pass


class RestClientConfigurationError(RestClientException):
    """wrapper exception"""

    pass


class RestClientValidationError(RestClientException):
    """wrapper exception"""

    pass


class RestClientQueryError(RestClientException):
    """wrapper exception"""

    pass


class InvalidTargetError(RestClientException):
    """An error when specifying an invalid target for a given REST API."""

    pass

    # def __init__(self, name, target):
    # """ InvalidTargetError constructor

    # :param name: The name of the REST API client
    # :type name: ``string``

    # :param target: The REST API target name
    # :type target: ``string``

    # """
    # super()"'{target}' is not a valid target for '{name}'".format(
    # target=target,
    # name=name
    # ))


class InvalidResourceError(RestClientException):
    """An error when specifying an invalid resource for a given REST API."""

    def __init__(self, name: str, resource: str):
        """InvalidResourceError constructor

        :param name: The name of the REST API client
        :param resource: The REST API resource name

        """
        response = f"'{resource}' is not a valid resource for '{name}'"
        super().__init__(response)


class RestResourceMissingContentError(RestClientResourceError):
    """wrapper exception"""

    pass


class RestTimeoutError(RestClientResourceError):
    """wrapper exception"""

    pass


class RestCredentailsError(RestClientResourceError):
    """wrapper exception"""

    pass


class RestResponseError(RestClientResourceError):
    """Exception due to a requests.Response whose status code indicates an error.

    :ivar response: Response object returned by the request

    """

    response: Response

    def __init__(self, response: Response, message: str):
        super().__init__(message)
        self.response = response


class RestAccessDeniedError(RestResponseError):
    def __init__(self, response: Response):
        super().__init__(
            response, f"error {response.status_code}: Access is denied to resource {response.url}"
        )


class RestBadRequestError(RestResponseError):
    def __init__(self, response: Response):
        super().__init__(response, f"Bad request for resource {response.url} ({response.reason})")


class RestInternalServerError(RestResponseError):
    def __init__(self, response: Response):
        super().__init__(
            response, f"error {response.status_code}: Internal Server error ({response.reason})"
        )


class RestResourceNotFoundError(RestResponseError):
    def __init__(self, response: Response):
        super().__init__(response, f"Object could not be found in database ({response.reason})")


class RestUnspecificResponseError(RestResponseError):
    def __init__(self, response: Response):
        super().__init__(response, f"REST error {response.status_code}: {response.reason}")


def raise_on_response_error(response: Response):
    """Raise custom exception for response status (code) 400 and higher.

    If the status code is below 400, this function calls
    response.raise_for_status and it is up to that function what to do.

    """
    if response.status_code < 400:
        response.raise_for_status()
    elif response.status_code == 400:
        raise RestBadRequestError(response)
    elif response.status_code in (401, 402, 403):
        raise RestAccessDeniedError(response)
    elif response.status_code == 404:
        raise RestResourceNotFoundError(response)
    elif response.status_code == 500:
        raise RestInternalServerError(response)
    else:
        raise RestUnspecificResponseError(response)
