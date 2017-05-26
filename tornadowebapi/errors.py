# -*- coding: utf-8 -*-
# Imported from flask-rest-jsonapi
# https://github.com/miLibris/flask-rest-jsonapi


def jsonapi_errors(jsonapi_errors):
    """Construct api error according to jsonapi 1.0

    Parameters
    ----------
    jsonapi_errors:
        an iterable of jsonapi error

    Returns
    -------
    dict
        a dict of errors according to jsonapi 1.0
    """
    return {'errors': [jsonapi_error for jsonapi_error in jsonapi_errors],
            'jsonapi': {'version': '1.0'}}


class Source:
    def __init__(self, pointer=None, parameter=None):
        self.pointer = pointer
        self.parameter = parameter

    def to_jsonapi(self):
        ret = {}
        if self.pointer is not None:
            ret["pointer"] = self.pointer

        if self.parameter is not None:
            ret["parameter"] = self.parameter

        return ret

    @classmethod
    def from_jsonapi(cls, d):
        return cls(**d)


class Error:
    def __init__(self,
                 source=None,
                 detail=None,
                 title=None,
                 status=None):
        """Initialize a jsonapi error object

        Parameters
        ----------
        source: Source
            the source object
        detail: str or None
            the detail of the error
        title: str or None
            The title of the error. By default, it's the title associated to
            the exception
        status: HTTPStatus enum
            The HTTP status of the error.
        """

        self.source = source
        self.detail = detail
        self.title = title
        self.status = status

    def to_jsonapi(self):
        ret = {}
        if self.status is not None:
            ret["status"] = str(self.status.value)

        if self.title is not None:
            ret['title'] = self.title

        if self.source is not None:
            ret["source"] = self.source.to_jsonapi()

        if self.detail is not None:
            ret['detail'] = self.detail

        return ret

    @classmethod
    def from_jsonapi(cls, d):
        source = d.get("source")
        if source is not None:
            d["source"] = Source.from_jsonapi(d["source"])

        return cls(**d)
