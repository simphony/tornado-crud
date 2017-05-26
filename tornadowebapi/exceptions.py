# Imported from flask-rest-jsonapi
# https://github.com/miLibris/flask-rest-jsonapi
import http.client

from tornadowebapi.errors import Error, Source


class JsonApiException(Exception):
    status = http.client.INTERNAL_SERVER_ERROR

    def __init__(self, errors):
        """Initialize a jsonapi exception

        Parameters
        ----------
        errors: List
            A list of Error objects
        """

        self.errors = errors

    def to_jsonapi(self):
        return [
            error.to_jsonapi()
            for error in self.errors
        ]


class BadRequest(JsonApiException):
    status = http.client.BAD_REQUEST

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Bad Request",
                            status=self.status)]

        super().__init__(errors)


class ValidationError(JsonApiException):
    status = http.client.UNPROCESSABLE_ENTITY

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Validation Error",
                            status=self.status)]

        super().__init__(errors)


class InvalidField(BadRequest):
    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Invalid fields querystring parameter",
                            source=Source(parameter="sort"),
                            status=self.status)]

        super().__init__(errors)


class InvalidInclude(BadRequest):
    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Invalid include querystring parameter",
                            source=Source(parameter="include"),
                            status=self.status)]

        super().__init__(errors)


class InvalidFilters(BadRequest):
    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Invalid filters querystring parameter",
                            source=Source(parameter="filters"),
                            status=self.status)]

        super().__init__(errors)


class InvalidSort(BadRequest):
    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Invalid sort querystring parameter",
                            source=Source(parameter="sort"),
                            status=self.status)]

        super().__init__(errors)


class ObjectNotFound(JsonApiException):
    status = http.client.NOT_FOUND

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Object not found",
                            status=self.status)]

        super().__init__(errors)


class RelatedObjectNotFound(ObjectNotFound):
    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Related object not found",
                            status=self.status)]

        super().__init__(errors)


class RelationNotFound(ObjectNotFound):
    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Relation object not found",
                            status=self.status)]

        super().__init__(errors)


class ObjectAlreadyPresent(JsonApiException):
    status = http.client.CONFLICT

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Object already present",
                            status=self.status)]

        super().__init__(errors)


class InvalidType(JsonApiException):
    status = http.client.CONFLICT

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Invalid type",
                            status=self.status)]

        super().__init__(errors)


class InvalidIdentifier(JsonApiException):
    status = http.client.CONFLICT

    def __init__(self, errors=None):
        if errors is None:
            errors = [Error(title="Invalid identifier",
                            status=self.status)]

        super().__init__(errors)
