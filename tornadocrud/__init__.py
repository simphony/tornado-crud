from .handler import ResourceHandler, CollectionHandler
from .utils import url_path_join, with_end_slash

MAJOR = 0
MINOR = 1
MICRO = 0
IS_RELEASED = False

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not IS_RELEASED:
    __version__ += '.dev0'


def api_handlers(base_urlpath, version="v1"):
    """Returns the API handlers for the REST interface.
    Add these handlers to your application to provide a
    REST interface to your Resources.


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
    return [
        (with_end_slash(
            url_path_join(base_urlpath, "api", version, "(.*)", "(.*)")),
         ResourceHandler
         ),
        (with_end_slash(
            url_path_join(base_urlpath, "api", version, "(.*)")),
         CollectionHandler
         ),
        ]