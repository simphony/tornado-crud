from .web_handlers import (
    ResourceWebHandler,
    CollectionWebHandler,
    JSAPIWebHandler)

from .transports import BasicRESTTransport
from .utils import url_path_join, with_end_slash
from .resource_handler import ResourceHandler
from .resource import Resource
from .singleton_resource import SingletonResource
from .authenticator import NullAuthenticator


class Registry:
    """Main class that registers the defined resources,
    and provides the appropriate handlers for tornado.

    It is also responsible for holding the authenticator,
    the renderer (converts internal representation to
    HTTP response payload) and the parser (converts HTTP
    request payload to internal representation).

    A registry is normally instantiated and held on the
    Tornado Application.
    """

    def __init__(self, transport=None):
        self._registered_handlers = {}
        self._authenticator = NullAuthenticator
        if transport is None:
            transport = BasicRESTTransport()
        self._transport = transport

    @property
    def authenticator(self):
        return self._authenticator

    @authenticator.setter
    def authenticator(self, authenticator):
        self._authenticator = authenticator

    @property
    def transport(self):
        """Returns the current transport."""
        return self._transport

    @property
    def registered_handlers(self):
        return self._registered_handlers

    def register(self, handler):
        """Registers a ResourceHandler.
        The associated resource will be used to determine the URL
        representing the resource collections. For example, a resource Image
        will have URLs of the type

        http://example.com/api/v1/images/identifier/

        Parameters
        ----------
        handler: ResourceHandler
            A subclass of the ResourceHandler

        Raises
        ------
        TypeError:
            if typ is not a subclass of Resource
        """
        if handler is None or not issubclass(handler, ResourceHandler):
            raise TypeError("handler must be a subclass of ResourceHandler")

        resource_class = handler.resource_class

        if resource_class is None:
            raise TypeError(
                "resource_class for handler {} must not be None".format(
                    handler
                ))

        if issubclass(resource_class, Resource):
            name = resource_class.collection_name()
        elif issubclass(resource_class, SingletonResource):
            name = resource_class.name()
        else:
            raise TypeError(
                "resource_class for handler {} must be a "
                "subtype of BaseResource. Found {}".format(
                    handler,
                    resource_class))

        if name in self._registered_handlers:
            raise ValueError(
                "Name {} is already in use by "
                "class {}, so it cannot be used by class {}".format(
                    name,
                    self._registered_handlers[name].__name__,
                    resource_class.__name__
                ))

        self._registered_handlers[name] = handler

    def __getitem__(self, collection_name):
        """Returns the class from the collection name with the
        indexing operator"""
        return self._registered_handlers[collection_name]

    def __contains__(self, item):
        """If the registry contains the given item"""
        return item in self._registered_handlers

    def api_handlers(self, base_urlpath, version="v1"):
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
        init_args = dict(
            registry=self,
            base_urlpath=base_urlpath,
            api_version=version,
        )

        return [
            (with_end_slash(
                url_path_join(base_urlpath, "api", version, "(.*)", "(.*)")),
             ResourceWebHandler,
             init_args
             ),
            (with_end_slash(
                url_path_join(base_urlpath, "api", version, "(.*)")),
             CollectionWebHandler,
             init_args
             ),
            (url_path_join(base_urlpath, "jsapi", version, "resources.js"),
             JSAPIWebHandler,
             init_args
             ),
        ]
