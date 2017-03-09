from .version import __version__ # noqa


def api_handlers(base_urlpath, version="v1"):
    """Returns the API handlers for the interface.
    Add these handlers to your application to provide an
    interface to your Resources.


    Parameters
    ----------
    base_urlpath: str
        The base url path to serve
    version: str
        A string identifying the version of the API.

    Notes
    -----
    The current implementation does not support multiple API versions yet.
    The version option is only provided for futureproofing.
    """
    from . import registry
    return registry.registry.api_handlers(base_urlpath, version)
