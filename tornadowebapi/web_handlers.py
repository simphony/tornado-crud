import contextlib


from tornado import gen, web, template, escape
from tornado.log import app_log
from tornado.web import HTTPError
from tornadowebapi.filtering import filter_spec_to_function
from tornadowebapi.schema import Schema
from tornadowebapi.singleton_schema import SingletonSchema
from tornadowebapi.traitlets import TraitError

from . import schema as resource_mod
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
            transport.serializer.serialize(exc))

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
            raise exceptions.Unable()

    def _check_resource_sanity(self, resource, scope):
        """Checks if a resource contains all the mandatory
        data. The response is different depending if the scope
        is input or output. In the first case, it's the client's fault (bad
        representation). In the second, it's the server's fault (internal
        error)
        """
        absents = resource_mod.mandatory_absents(resource, scope)
        if len(absents) != 0:
            if scope == "input":
                raise exceptions.BadRepresentation(
                    message="Missing mandatory elements: {}".format(absents))
            elif scope == "output":
                self.log.error(
                    "Returned resource {} had missing mandatory elements "
                    "in get: {}".format(resource, absents)
                    )
                raise exceptions.Unable()
            else:
                # Should never get here, because mandatory_absents does it too.
                raise ValueError(
                    "scope must be either input or output")  # pragma: no cover

    @contextlib.contextmanager
    def exceptions_to_http(self,
                           res_handler,
                           handler_method,
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
                res_handler, identifier, handler_method,
                type(e), str(e)
            ))
            raise self.to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error on {} {} {}".format(
                    res_handler, identifier, handler_method
                ))
            if on_generic_raise is None:
                raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)
            else:
                raise on_generic_raise

    def parsed_query_arguments(self):
        """Converts the query arguments to a dict. This works around
        a limitation of tornado that does not provide a direct interface
        to this service.
        """
        ret = {}
        arguments = self.request.query_arguments

        for key in arguments.keys():
            value = self.get_query_arguments(key)
            # They are all lists. If they have one element, extract it
            # and put it as the value. If they are empty, remove the key
            if len(value) == 0:
                continue
            elif len(value) == 1:
                ret[key] = value[0]
            else:
                ret[key] = value

            # We consider these specials (as they are passed to items())
            # and convert them to integers
            if key in ["limit", "offset"]:
                try:
                    ret[key] = int(ret[key])
                except Exception:
                    raise web.HTTPError(httpstatus.BAD_REQUEST)
            elif key == "filter":
                try:
                    filter_spec = escape.json_decode(ret["filter"])
                except Exception:
                    raise web.HTTPError(httpstatus.BAD_REQUEST)

                if isinstance(filter_spec, (list, dict)):
                    ret["filter_"] = filter_spec_to_function(filter_spec)

                # We remove the original filter option because filter
                # is a python function and we want to reduce chances of
                # collision.
                del ret["filter"]

        return ret

    def _send_to_client(self, entity):
        """Convenience method to send a given entity to a client.
        Serializes it and puts the right headers.
        If entity is None, sets no content http response."""
        if entity is None:
            self.clear_header('Content-Type')
            self.set_status(httpstatus.NO_CONTENT)
            return

        self.set_status(httpstatus.OK)
        # Need to convert into a dict for security issue tornado/1009
        transport = self._registry.transport
        self.write(
            transport.renderer.render(
                transport.serializer.serialize(
                    entity)
            )
        )
        self.set_header("Content-Type", transport.content_type)
        self.flush()

    def _send_created_to_client(self, resource):
        """Sends a created message to the client for a given resource"""
        if isinstance(resource, Schema):
            location = with_end_slash(
                url_path_join(self.request.full_url(),
                              str(resource.identifier)))
        elif isinstance(resource, SingletonSchema):
            location = with_end_slash(self.request.full_url())
        else:
            raise TypeError("Invalid resource type {}".format(resource))

        self.set_status(httpstatus.CREATED)
        self.set_header("Location", location)
        self.clear_header('Content-Type')
        self.flush()


class WithoutIdentifierWebHandler(BaseWebHandler):
    """Handler for URLs without an identifier.
    """
    @gen.coroutine
    def get(self, name):
        res_handler = self.get_resource_handler_or_404(name)
        args = self.parsed_query_arguments()

        if res_handler.handles_singleton():
            subcoro = self._get_singleton
        else:
            subcoro = self._get_collection

        yield subcoro(res_handler, args)

    @gen.coroutine
    def _get_collection(self, res_handler, args):
        """Returns the collection of available items"""

        items_response = ItemsResponse(res_handler.resource_class)

        with self.exceptions_to_http(res_handler, "get"):
            yield res_handler.items(items_response, **args)

        for resource in items_response.items:
            self._check_none(resource.identifier,
                             "identifier",
                             "items")
            self._check_resource_sanity(resource, "output")

        self._send_to_client(items_response)

    @gen.coroutine
    def _get_singleton(self, res_handler, args):
        transport = self._registry.transport

        with self.exceptions_to_http(res_handler, "get"):
            resource = transport.deserializer.deserialize(
                res_handler.resource_class)

            yield res_handler.retrieve(resource, **args)

            self._check_resource_sanity(resource, "output")

        self._send_to_client(resource)

    @gen.coroutine
    def post(self, name):
        res_handler = self.get_resource_handler_or_404(name)
        args = self.parsed_query_arguments()

        if res_handler.handles_singleton():
            subcoro = self._post_singleton
        else:
            subcoro = self._post_collection

        yield subcoro(res_handler, args)

    @gen.coroutine
    def _post_collection(self, res_handler, args):
        """Creates a new resource in the collection."""
        transport = self._registry.transport
        payload = self.request.body

        with self.exceptions_to_http(res_handler, "post"):
            representation = transport.parser.parse(payload)

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation("Generic exception "
                                         "during preprocessing"))

        with self.exceptions_to_http(res_handler, "post",
                                     on_generic_raise=on_generic_raise):
            representation = res_handler.preprocess_representation(
                representation)

            self._check_none(representation,
                             "representation",
                             "preprocess_representation")

        with self.exceptions_to_http(res_handler, "post"):
            try:
                resource = transport.deserializer.deserialize(
                    res_handler.resource_class,
                    None,
                    representation,
                )
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_resource_sanity(resource, "input")

            yield res_handler.create(resource, **args)

            self._check_none(resource.identifier,
                             "resource_id",
                             "create()")

        self._send_created_to_client(resource)

    @gen.coroutine
    def _post_singleton(self, res_handler, args):
        """POST on a singleton creates the resource and fills the information
        if the resource is not there. If it's there, will return a conflict."""
        transport = self._registry.transport
        payload = self.request.body

        with self.exceptions_to_http(res_handler, "post"):
            representation = transport.parser.parse(payload)

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation("Generic exception "
                                         "during preprocessing"))

        with self.exceptions_to_http(res_handler, "post",
                                     on_generic_raise=on_generic_raise):
            representation = res_handler.preprocess_representation(
                representation)

            self._check_none(representation,
                             "representation",
                             "preprocess_representation")

        with self.exceptions_to_http(res_handler, "post"):
            try:
                resource = transport.deserializer.deserialize(
                    res_handler.resource_class,
                    None,
                    representation,
                )
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_resource_sanity(resource, "input")

            exists = yield res_handler.exists(resource)

            if exists:
                raise exceptions.Exists()

            yield res_handler.create(resource, **args)

        self._send_created_to_client(resource)

    @gen.coroutine
    def put(self, name):
        res_handler = self.get_resource_handler_or_404(name)
        args = self.parsed_query_arguments()

        if res_handler.handles_singleton():
            coro = self._put_singleton
        else:
            coro = self._put_collection

        yield coro(res_handler, args)

    @gen.coroutine
    def _put_collection(self, res_handler, args):
        """You cannot PUT on a collection"""
        raise HTTPError(httpstatus.METHOD_NOT_ALLOWED)

    @gen.coroutine
    def _put_singleton(self, res_handler, args):
        """Replaces the resource with a new representation."""
        transport = self._registry.transport

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation("Generic exception during "
                                         "deserialization"))
        with self.exceptions_to_http(res_handler,
                                     "put",
                                     on_generic_raise=on_generic_raise):
            try:
                resource = transport.deserializer.deserialize(
                    res_handler.resource_class,
                    None,
                    transport.parser.parse(self.request.body))
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_none(resource,
                             "representation",
                             "deserialize")

        with self.exceptions_to_http(res_handler, "put"):
            self._check_resource_sanity(resource, "input")

            yield res_handler.update(resource, **args)

        self._send_to_client(None)

    @gen.coroutine
    def delete(self, name):
        res_handler = self.get_resource_handler_or_404(name)
        args = self.parsed_query_arguments()

        if res_handler.handles_singleton():
            coro = self._delete_singleton
        else:
            coro = self._delete_collection

        yield coro(res_handler, args)

    @gen.coroutine
    def _delete_collection(self, res_handler, args):
        raise HTTPError(httpstatus.METHOD_NOT_ALLOWED)

    @gen.coroutine
    def _delete_singleton(self, res_handler, args):
        """Deletes the singleton resource."""
        transport = self._registry.transport

        with self.exceptions_to_http(res_handler, "delete"):
            resource = transport.deserializer.deserialize(
                res_handler.resource_class)

            yield res_handler.delete(resource, **args)

        self._send_to_client(None)


class WithIdentifierWebHandler(BaseWebHandler):
    """Handler for URLs addressing a resource.
    """
    @gen.coroutine
    def get(self, collection_name, identifier):
        """Retrieves the resource representation."""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("get",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        with self.exceptions_to_http("get", collection_name, identifier):
            resource = transport.deserializer.deserialize(
                res_handler.resource_class,
                identifier)

            self._check_none(identifier, "identifier", "preprocess_identifier")

            yield res_handler.retrieve(resource, **args)

            self._check_resource_sanity(resource, "output")

        self._send_to_client(resource)

    @gen.coroutine
    def post(self, collection_name, identifier):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("post",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        with self.exceptions_to_http("post", collection_name, identifier):
            self._check_none(identifier, "identifier", "preprocess_identifier")

            resource = transport.deserializer.deserialize(
                res_handler.resource_class,
                identifier)

            exists = yield res_handler.exists(resource, **args)

        if exists:
            raise web.HTTPError(httpstatus.CONFLICT)
        else:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    @gen.coroutine
    def put(self, collection_name, identifier):
        """Replaces the resource with a new representation."""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("put",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation(
                "Generic exception during preprocessing of {}".format(
                    collection_name)))
        with self.exceptions_to_http("put",
                                     collection_name,
                                     identifier,
                                     on_generic_raise=on_generic_raise):
            self._check_none(identifier, "identifier", "preprocess_identifier")

            try:
                resource = transport.deserializer.deserialize(
                    res_handler.resource_class,
                    identifier,
                    transport.parser.parse(self.request.body))
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_none(resource,
                             "representation",
                             "preprocess_representation")

        with self.exceptions_to_http("put",
                                     collection_name,
                                     identifier):
            self._check_resource_sanity(resource, "input")

            yield res_handler.update(resource, **args)

        self._send_to_client(None)

    @gen.coroutine
    def delete(self, collection_name, identifier):
        """Deletes the resource."""
        res_handler = self.get_resource_handler_or_404(collection_name)
        transport = self._registry.transport
        args = self.parsed_query_arguments()

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

            resource = transport.deserializer.deserialize(
                res_handler.resource_class,
                identifier)

            yield res_handler.delete(resource, **args)

        self._send_to_client(None)


class JSAPIWebHandler(BaseWebHandler):
    """Handles the JavaScript API request."""
    @gen.coroutine
    def get(self):
        resources = []
        reg = self.registry
        for resource_handler in reg.registered_handlers.values():
            class_name = resource_handler.resource_class.__name__
            bound_name = resource_handler.bound_name()

            resources.append({
                "class_name": class_name,
                "bound_name": bound_name,
                "singleton": resource_handler.handles_singleton()
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
