from typing import Dict


class StreambirdException(Exception):
    """Generic StreambirdException class"""

    code = None

    def __init__(self, message, errcode=None):
        if not message:
            message = type(self).__name__
        self.message = message

        if errcode:
            self.code = errcode

        if self.code:
            super().__init__(f"<Response [{self.code}]> {message}")
        else:
            super().__init__(f"<Response> {message}")


class StreambirdInvalidRequest(StreambirdException):
    """400 - Bad Request -- The request was unacceptable,
    often due to missing a required parameter.
    """

    code = 400


class StreambirdUnauthorized(StreambirdException):
    """401 - Unauthorized -- No valid API key provided."""

    code = 401


class StreambirdNotEnabled(StreambirdException):
    """402 - Not enabled -- Please contact sales@streambird.com before
    creating this type of task.
    """

    code = 402


class StreambirdResourceNotFound(StreambirdException):
    """404 - Not Found -- The requested resource doesn't exist."""

    code = 404


class StreambirdDuplicateResource(StreambirdException):
    """409 - Conflict -- Object already exists with same name,
    idempotency key or unique_id.
    """

    code = 409


class StreambirdTooManyRequests(StreambirdException):
    """429 - Too Many Requests -- Too many requests hit the API
    too quickly.
    """

    code = 429


class StreambirdInternalError(StreambirdException):
    """500 - Internal Server Error -- We had a problem with our server.
    Try again later.
    """

    code = 500


class StreambirdServiceUnavailable(StreambirdException):
    """503 - Server Timeout From Request Queueing -- Try again later."""

    code = 503


class StreambirdTimeoutError(StreambirdException):
    """504 - Server Timeout Error -- Try again later."""

    code = 504


ExceptionMap: Dict[int, StreambirdException] = {
    StreambirdInvalidRequest.code: StreambirdInvalidRequest,
    StreambirdUnauthorized.code: StreambirdUnauthorized,
    StreambirdNotEnabled.code: StreambirdNotEnabled,
    StreambirdResourceNotFound.code: StreambirdResourceNotFound,
    StreambirdDuplicateResource.code: StreambirdDuplicateResource,
    StreambirdTooManyRequests.code: StreambirdTooManyRequests,
    StreambirdInternalError.code: StreambirdInternalError,
    StreambirdTimeoutError.code: StreambirdTimeoutError,
    StreambirdServiceUnavailable.code: StreambirdServiceUnavailable,
}
