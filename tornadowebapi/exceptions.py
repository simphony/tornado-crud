# Imported from flask-rest-jsonapi
# https://github.com/miLibris/flask-rest-jsonapi

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


class NotFound(WebAPIException):
    """Exception raised when the resource is not found.
    Raise this exception in your handlers when you can't
    find the resource the identifier refers to.
    """
    http_code = httpstatus.NOT_FOUND


class Exists(WebAPIException):
    """Represents a case where the resource could not be created
    because it already exists. This is generally raised in the
    create() method if the resource has uniqueness constraints on
    things other than the exposed id."""

    http_code = httpstatus.CONFLICT


class BadRepresentation(WebAPIException):
    """Exception raised when the resource representation is
    invalid or does not contain the appropriate keys.
    Raise this exception in your handlers when the received
    representation is ill-formed
    """
    http_code = httpstatus.BAD_REQUEST


class BadQueryArguments(WebAPIException):
    """Exception raised when the query arguments do not conform to the
    expected format.
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


class JsonApiException(Exception):

    title = 'Unknown error'
    status = 500

    def __init__(self, source, detail, title=None, status=None):
        """Initialize a jsonapi exception

        :param dict source: the source of the error
        :param str detail: the detail of the error
        """
        self.source = source
        self.detail = detail
        if title is not None:
            self.title = title
        if status is not None:
            self.status = status

    def to_dict(self):
        return {'status': self.status,
                'source': self.source,
                'title': self.title,
                'detail': self.detail}


class BadRequest_(JsonApiException):
    title = "Bad request"
    status = 400


class InvalidField(BadRequest):
    title = "Invalid fields querystring parameter."

    def __init__(self, detail):
        self.source = {'parameter': 'fields'}
        self.detail = detail


class InvalidInclude(BadRequest):
    title = "Invalid include querystring parameter."

    def __init__(self, detail):
        self.source = {'parameter': 'include'}
        self.detail = detail


class InvalidFilters(BadRequest):
    title = "Invalid filters querystring parameter."

    def __init__(self, detail):
        self.source = {'parameter': 'filters'}
        self.detail = detail


class InvalidSort(BadRequest):
    title = "Invalid sort querystring parameter."

    def __init__(self, detail):
        self.source = {'parameter': 'sort'}
        self.detail = detail


class ObjectNotFound(JsonApiException):
    title = "Object not found"
    status = 404


class RelatedObjectNotFound(ObjectNotFound):
    title = "Related object not found"


class RelationNotFound(JsonApiException):
    title = "Relation not found"


class InvalidType(JsonApiException):
    title = "Invalid type"
    status = 409
