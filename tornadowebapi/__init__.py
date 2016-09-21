from . import registry

MAJOR = 0
MINOR = 2
MICRO = 0
IS_RELEASED = False

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not IS_RELEASED:
    __version__ += '.dev0'


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
    return registry.registry.api_handlers(base_urlpath, version)
