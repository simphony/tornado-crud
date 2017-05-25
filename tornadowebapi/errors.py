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
