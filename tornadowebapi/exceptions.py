# Imported from flask-rest-jsonapi
# https://github.com/miLibris/flask-rest-jsonapi
import http.client


class JsonApiException(Exception):
    title = 'Unknown error'
    status = http.client.INTERNAL_SERVER_ERROR

    def __init__(self, source, detail, title=None, status=None):
        """Initialize a jsonapi exception

        Parameters
        ----------
        source: dict
            the source of the error
        detail: str
            the detail of the error
        """
        self.source = source
        self.detail = detail
        if title is not None:
            self.title = title
        if status is not None:
            self.status = status

    def to_dict(self):
        return {'status': self.status.value,
                'source': self.source,
                'title': self.title,
                'detail': self.detail
                }


class BadRequest(JsonApiException):
    title = "Bad request"
    status = http.client.BAD_REQUEST


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
    status = http.client.NOT_FOUND


class RelatedObjectNotFound(ObjectNotFound):
    title = "Related object not found"


class RelationNotFound(JsonApiException):
    title = "Relation not found"


class ObjectAlreadyPresent(JsonApiException):
    title = "Object already present"
    status = http.client.CONFLICT


class InvalidType(JsonApiException):
    title = "Invalid type"
    status = http.client.CONFLICT
