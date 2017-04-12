import contextlib

from tornado import gen, web, template
from tornado.log import app_log

from . import resource as resource_mod
from . import exceptions
from .items_response import ItemsResponse
from .http import httpstatus
from .http.payloaded_http_error import PayloadedHTTPError
from .utils import url_path_join, with_end_slash


class BaseWebHandler(web.RequestHandler):
    def initialize(self, registry, base_urlpath, api_version):
        """Initialization method for when the class is instantiated."""
        self._registry = registry
        self._base_urlpath = base_urlpath
        self._api_version = api_version

    @gen.coroutine
    def prepare(self):
        """Runs before any specific handler. """
        authenticator = self.registry.authenticator
        self.current_user = yield authenticator.authenticate(self)

    @property
    def registry(self):
        """Returns the class vs Resource registry"""
        return self._registry

    @property
    def base_urlpath(self):
        """Returns the Base urlpath as from initial setup"""
        return self._base_urlpath

    @property
    def api_version(self):
        """Returns the API version this handler is taking care of
        """
        return self._api_version

    @property
    def log(self):
        return app_log

    def get_resource_handler_or_404(self, collection_name):
        """Given a collection name, inquires the registry
        for its associated Resource class. If not found
        raises HTTPError(NOT_FOUND)"""

        try:
            resource_class = self.registry[collection_name]
            return resource_class(
                application=self.application,
                current_user=self.current_user)
        except KeyError:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    def write_error(self, status_code, **kwargs):
        """Provides appropriate payload to the response in case of error.
        """
        exc_info = kwargs.get("exc_info")

        if exc_info is None:
            self.clear_header('Content-Type')
            self.finish()

        exc = exc_info[1]

        if isinstance(exc, PayloadedHTTPError) and exc.payload is not None:
            self.set_header('Content-Type', exc.content_type)
            self.finish(exc.payload)
        else:
            # For non-payloaded http errors or any other exception
            # we don't want to return anything as payload.
            # The error code is enough.
            self.clear_header('Content-Type')
            self.finish()

    def to_http_exception(self, exc):
        """Converts a REST exception into the appropriate HTTP one."""

        transport = self._registry.transport
        payload = transport.renderer.render(
            transport.serializer.serialize_exception(exc))

        if payload is not None:
            return PayloadedHTTPError(
                status_code=exc.http_code,
                payload=payload,
                content_type=transport.content_type
            )
        else:
            return web.HTTPError(exc.http_code)

    def _check_none(self, entity, entity_name, culprit_routine):
        """Check if entity is None. If it is, raises INTERNAL_SERVER_ERROR.
        entity_name is the name of the entity for the log message.
        culprit_routine is the routine that returned None.
        """
        if entity is None:
            self.log.error(
                "{entity_name} is None. "
                "Is {culprit_routine} not returning anything?".format(
                    entity_name=entity_name,
                    culprit_routine=culprit_routine
                ))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

    @contextlib.contextmanager
    def exceptions_to_http(self,
                           handler_method,
                           collection_name,
                           identifier=None,
                           on_generic_raise=None):
        """Convenience method to reduce clutter due to exception handling.
        On a generic exception (e.g. KeyError, IndexError, etc...), raises
        on_generic_raise, or if not defined, a simple internal server error.
        Any exception created within this context manager will eventually
        be converted into a HTTPError or PayloadedHTTPError.
        """
        try:
            yield
        except web.HTTPError:
            raise
        except exceptions.WebAPIException as e:
            self.log.error("Web API exception on {} {} {}: {} {}".format(
                collection_name, identifier, handler_method, type(e), str(e)
            ))
            raise self.to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during {} on {} {}".format(
                    handler_method,
                    collection_name,
                    identifier
                ))
            if on_generic_raise is None:
                raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)
            else:
                raise on_generic_raise


class CollectionWebHandler(BaseWebHandler):
    """Handler for URLs addressing a collection.
    """
    @gen.coroutine
    def get(self, collection_name):
        """Returns the collection of available items"""
        res_handler = self.get_resource_handler_or_404(collection_name)

        with self.exceptions_to_http("get", collection_name):
            items_response = yield res_handler.items()

        # If it's a list, it's the full deal.
        # Convert it in a trivial ItemsResponse for ease of handling
        if isinstance(items_response, list):
            response = ItemsResponse()
            response.items = items_response
            response.index_first = 0
            response.num_items = response.total_items = len(items_response)

            items_response = response

        if not isinstance(items_response, ItemsResponse):
            self.log.error(
                "Internal error during get operation on {}."
                "items() returned {}, not ItemsResponse or list".format(
                    collection_name,
                    type(items_response)))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        for entry in items_response.items:
            if not isinstance(entry, res_handler.resource_class):
                self.log.error(
                    "Internal error during get operation on {}. "
                    "items() returned a list with objects different from "
                    "the declared type. Got {} instead of {}".format(
                        collection_name,
                        entry.__class__,
                        res_handler.resource_class
                    ))
                raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.set_status(httpstatus.OK)
        # Need to convert into a dict for security issue tornado/1009
        transport = self._registry.transport
        self.write(
            transport.renderer.render(
                transport.serializer.serialize_items_response(
                    items_response)
            )
        )
        self.set_header("Content-Type", transport.content_type)
        self.flush()

    @gen.coroutine
    def post(self, collection_name):
        """Creates a new resource in the collection."""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport
        payload = self.request.body

        with self.exceptions_to_http("post", collection_name):
            representation = transport.parser.parse(payload)

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation(
                "Generic exception during preprocessing of {}".format(
                    collection_name)))

        with self.exceptions_to_http("post", collection_name,
                                     on_generic_raise=on_generic_raise):
            representation = res_handler.preprocess_representation(
                representation)

        self._check_none(representation,
                         "representation",
                         "{}.preprocess_representation".format(
                             collection_name))

        with self.exceptions_to_http("post", collection_name):
            resource = transport.deserializer.deserialize_resource(
                res_handler.resource_class,
                None,
                representation,
            )

            absents = resource_mod.mandatory_absents(resource)
            if len(absents) != 0:
                raise exceptions.BadRepresentation(
                    message="Missing mandatory elements: {}".format(absents))

            resource_id = yield res_handler.create(resource)

        self._check_none(resource_id,
                         "resource_id",
                         "{}.create()".format(collection_name))

        location = with_end_slash(
            url_path_join(self.request.full_url(), str(resource_id)))

        self.set_status(httpstatus.CREATED)
        self.set_header("Location", location)
        self.clear_header('Content-Type')
        self.flush()


class ResourceWebHandler(BaseWebHandler):
    """Handler for URLs addressing a resource.
    """
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    @gen.coroutine
    def get(self, collection_name, identifier):
        """Retrieves the resource representation."""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport

        with self.exceptions_to_http("get",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        self._check_none(identifier, "identifier", "preprocess_identifier")

        with self.exceptions_to_http("get",
                                     collection_name,
                                     identifier):
            resource = transport.deserializer.deserialize_resource(
                res_handler.resource_class,
                identifier,
                None)
            yield res_handler.retrieve(resource)

            absents = resource_mod.mandatory_absents(resource)
            if len(absents) != 0:
                self.log.error(
                    "Returned resource {} {} had missing mandatory elements "
                    "in get: {}".format(
                        collection_name,
                        identifier,
                        absents
                    ))
                raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.set_status(httpstatus.OK)
        transport = self._registry.transport
        self.write(
            transport.renderer.render(
                transport.serializer.serialize_resource(resource)
            ))
        self.set_header("Content-Type", transport.content_type)
        self.flush()

    @gen.coroutine
    def post(self, collection_name, identifier):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport

        with self.exceptions_to_http("post",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        self._check_none(identifier, "identifier", "preprocess_identifier")

        with self.exceptions_to_http("post", collection_name, identifier):
            resource = transport.deserializer.deserialize_resource(
                res_handler.resource_class,
                identifier,
                None)
            exists = yield res_handler.exists(resource)

        if exists:
            raise web.HTTPError(httpstatus.CONFLICT)
        else:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    @gen.coroutine
    def put(self, collection_name, identifier):
        """Replaces the resource with a new representation."""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport

        with self.exceptions_to_http("put",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        self._check_none(identifier, "identifier", "preprocess_identifier")

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation(
                "Generic exception during preprocessing of {}".format(
                    collection_name)))
        with self.exceptions_to_http("put",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=on_generic_raise):
            resource = transport.deserializer.deserialize_resource(
                res_handler.resource_class,
                identifier,
                transport.parser.parse(self.request.body))

        self._check_none(resource,
                         "representation",
                         "preprocess_representation")

        with self.exceptions_to_http("put",
                                     collection_name,
                                     identifier):
            absents = resource_mod.mandatory_absents(resource)
            if len(absents) != 0:
                raise exceptions.BadRepresentation(
                    message="Missing mandatory elements: {}".format(absents))

            yield res_handler.update(resource)

        self.clear_header('Content-Type')
        self.set_status(httpstatus.NO_CONTENT)

    @gen.coroutine
    def delete(self, collection_name, identifier):
        """Deletes the resource."""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport

        with self.exceptions_to_http("delete",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        self._check_none(identifier, "identifier", "preprocess_identifier")

        with self.exceptions_to_http("delete",
                                     collection_name,
                                     identifier):
            resource = transport.deserializer.deserialize_resource(
                res_handler.resource_class,
                identifier,
                None)
            yield res_handler.delete(resource)

        self.clear_header('Content-Type')
        self.set_status(httpstatus.NO_CONTENT)


class JSAPIWebHandler(BaseWebHandler):
    """Handles the JavaScript API request."""
    @gen.coroutine
    def get(self):
        resources = []
        reg = self.registry
        for coll_name, resource_handler in reg.registered_handlers.items():
            class_name = resource_handler.resource_class.__name__

            resources.append({
                "class_name": class_name,
                "collection_name": coll_name,
            })
        self.set_header("Content-Type", "application/javascript")
        self.render("templates/resources.template.js",
                    base_urlpath=self.base_urlpath,
                    api_version=self.api_version,
                    resources=resources)

    def create_template_loader(self, template_path):
        """Ovberride the default template loader, because if
        any code overrides the template loader in the settings,
        we don't want to rely on that. We want to be sure we use
        the tornado loader."""
        return template.Loader(template_path, whitespace='all')

    def get_template_path(self):
        """Override the path to make sure we search relative to this file
        """
        return None
