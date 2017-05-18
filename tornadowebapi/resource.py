import contextlib

from tornado import web, gen, escape
from tornado.log import app_log
from tornadowebapi import exceptions
from tornadowebapi.filtering import filter_spec_to_function
from tornadowebapi.http import httpstatus
from tornadowebapi.http.payloaded_http_error import PayloadedHTTPError
from tornadowebapi.schema import Schema, mandatory_absents
from tornadowebapi.singleton_schema import SingletonSchema
from tornadowebapi.utils import with_end_slash, url_path_join


class Resource(web.RequestHandler):
    model_connector = None
    schema = None

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

    def get_model_connector(self):
        return self.model_connector(
            application=self.application,
            current_user=self.current_user)

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
        absents = mandatory_absents(resource, scope)
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

    @classmethod
    def is_singleton(cls):
        """Returns true if the handler resource_class is a singleton class.
        Returns false otherwise."""
        schema = cls.schema

        if schema is None:
            raise TypeError(
                "schema for handler {} must not be None".format(
                    cls
                ))

        if issubclass(schema, Schema):
            return False
        elif issubclass(schema, SingletonSchema):
            return True

        raise TypeError(
            "schema for handler {} must be a "
            "subtype of BaseResource. Found {}".format(
                cls,
                schema))

    @classmethod
    def bound_name(cls):
        """Returns the name under which the resource will be presented as
        a URL /name/.
        This passes through the call to its name if singleton,
        or to the collection name if not.
        """
        schema = cls.schema
        if cls.is_singleton():
            return schema.name()
        else:
            return schema.collection_name()

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
