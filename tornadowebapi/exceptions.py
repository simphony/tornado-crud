from .http import httpstatus


class WebAPIException(Exception):
    """Base exception for the REST infrastructure
    These are exceptions that can be raised by the handlers.
    """
    #: HTTP code generally associated to this exception.
    #: Missing any better info, default is a server error.
    http_code = httpstatus.INTERNAL_SERVER_ERROR

    def __init__(self, message=None, **kwargs):
        """Initializes the exception. keyword arguments will become
        part of the representation as key/value pairs."""
        super().__init__(message)
        self.message = message
        self.info = kwargs if len(kwargs) else None

    def representation(self):
        """Returns a dictionary with the representation of the exception.
        """
        data = {
            "type": type(self).__name__
        }
        if self.message is not None:
            data["message"] = self.message

        if self.info is not None:
            data.update(self.info)

        return data


class NotFound(WebAPIException):
    """Exception raised when the resource is not found.
    Raise this exception in your handlers when you can't
    find the resource the identifier refers to.
    """
    http_code = httpstatus.NOT_FOUND

    def representation(self):
        """NotFound is special as it does not have a representation,
        just an error status"""
        return None


class Exists(WebAPIException):
    """Represents a case where the resource could not be created
    because it already exists. This is generally raised in the
    create() method if the resource has uniqueness constraints on
    things other than the exposed id."""

    http_code = httpstatus.CONFLICT

    def representation(self):
        """Exists does not have a representation, just an error status"""
        return None


class BadRepresentation(WebAPIException):
    """Exception raised when the resource representation is
    invalid or does not contain the appropriate keys.
    Raise this exception in your handlers when the received
    representation is ill-formed
    """
    http_code = httpstatus.BAD_REQUEST


class BadRequest(WebAPIException):
    """Deprecated. Kept for compatibility. Use BadRepresentation."""
    http_code = httpstatus.BAD_REQUEST


class Unable(WebAPIException):
    """Exception raised when the request cannot be performed
    for whatever reason that is not dependent on the client.
    """
    http_code = httpstatus.INTERNAL_SERVER_ERROR
