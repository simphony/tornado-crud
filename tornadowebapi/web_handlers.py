from tornado import gen, web, escape, template
from tornado.log import app_log

from . import exceptions
from .http import httpstatus
from .http.payloaded_http_error import PayloadedHTTPError
from .utils import url_path_join, with_end_slash


class BaseHandler(web.RequestHandler):
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

        representation = exc.representation()
        payload = None
        content_type = None

        if representation is not None:
            payload = escape.json_encode(representation)
            content_type = "application/json"

        return PayloadedHTTPError(
            status_code=exc.http_code,
            payload=payload,
            content_type=content_type
        )

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


class CollectionWebHandler(BaseHandler):
    """Handler for URLs addressing a collection.
    """
    @gen.coroutine
    def get(self, collection_name):
        """Returns the collection of available items"""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            items = yield res_handler.items()
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during get operation on {}".format(
                    collection_name,
                ))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.set_status(httpstatus.OK)
        # Need to convert into a dict for security issue tornado/1009
        self.write({"items": [str(item) for item in items]})
        self.flush()

    @gen.coroutine
    def post(self, collection_name):
        """Creates a new resource in the collection."""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            decoded_rep = escape.json_decode(self.request.body)
            representation = res_handler.validate_representation(decoded_rep)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except Exception:
            self.log.exception("invalid payload received.")
            raise web.HTTPError(httpstatus.BAD_REQUEST)

        self._check_none(representation,
                         "representation",
                         "validate_representation")

        try:
            resource_id = yield res_handler.create(representation)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during post operation on {}".format(
                    collection_name,
                ))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self._check_none(resource_id,
                         "resource_id",
                         "{}.create()".format(collection_name))

        location = with_end_slash(
            url_path_join(self.request.full_url(), str(resource_id)))

        self.set_status(httpstatus.CREATED)
        self.set_header("Location", location)
        self.clear_header('Content-Type')
        self.flush()


class ResourceWebHandler(BaseHandler):
    """Handler for URLs addressing a resource.
    """
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    @gen.coroutine
    def get(self, collection_name, identifier):
        """Retrieves the resource representation."""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            identifier = res_handler.validate_identifier(identifier)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except Exception:
            raise web.HTTPError(httpstatus.NOT_FOUND)

        self._check_none(identifier, "identifier", "validate_identifier")

        try:
            representation = yield res_handler.retrieve(identifier)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during get of {}/{}".format(
                    collection_name,
                    identifier))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.set_status(httpstatus.OK)
        self.write(representation)
        self.flush()

    @gen.coroutine
    def post(self, collection_name, identifier):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            identifier = res_handler.validate_identifier(identifier)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except Exception:
            raise web.HTTPError(httpstatus.NOT_FOUND)

        self._check_none(identifier, "identifier", "validate_identifier")

        try:
            exists = yield res_handler.exists(identifier)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during post of {}/{}".format(
                    collection_name,
                    identifier))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        if exists:
            raise web.HTTPError(httpstatus.CONFLICT)
        else:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    @gen.coroutine
    def put(self, collection_name, identifier):
        """Replaces the resource with a new representation."""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            decoded = escape.json_decode(self.request.body)
            representation = res_handler.validate_representation(decoded)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except Exception:
            raise web.HTTPError(httpstatus.BAD_REQUEST)

        self._check_none(representation,
                         "representation",
                         "validate_representation")

        try:
            identifier = res_handler.validate_identifier(identifier)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except Exception:
            raise web.HTTPError(httpstatus.NOT_FOUND)

        self._check_none(identifier, "identifier", "validate_identifier")

        try:
            yield res_handler.update(identifier, representation)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during put of {}/{}".format(
                    collection_name,
                    identifier))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.clear_header('Content-Type')
        self.set_status(httpstatus.NO_CONTENT)

    @gen.coroutine
    def delete(self, collection_name, identifier):
        """Deletes the resource."""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            identifier = res_handler.validate_identifier(identifier)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except Exception:
            raise web.HTTPError(httpstatus.NOT_FOUND)

        self._check_none(identifier, "identifier", "validate_identifier")

        try:
            yield res_handler.delete(identifier)
        except exceptions.WebAPIException as e:
            raise self.to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during delete of {}/{}".format(
                    collection_name,
                    identifier))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.clear_header('Content-Type')
        self.set_status(httpstatus.NO_CONTENT)


class JSAPIHandler(BaseHandler):
    """Handles the JavaScript API request."""
    @gen.coroutine
    def get(self):
        resources = []
        for coll_name, resource in self.registry.registered_types.items():
            resources.append({
                "class_name": resource.__name__,
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
