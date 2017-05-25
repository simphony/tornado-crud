import http.client

from tornado import web, gen, escape
from tornado.log import app_log
from tornadowebapi import exceptions
from tornadowebapi.errors import jsonapi_errors
from tornadowebapi.utils import with_end_slash, url_path_join


_CONTENT_TYPE_JSONAPI = 'application/vnd.api+json'


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

        if isinstance(exc, exceptions.JsonApiException):
            self.set_header('Content-Type', _CONTENT_TYPE_JSONAPI)
            self.finish(escape.json_encode(jsonapi_errors(exc.to_dict())))
        else:
            # For non-payloaded http errors or any other exception
            # we don't want to return anything as payload.
            # The error code is enough.
            self.clear_header('Content-Type')
            self.finish()

    def _send_to_client(self, entity):
        """Convenience method to send a given entity to a client.
        Serializes it and puts the right headers.
        If entity is None, sets no content http response."""

        if entity is None:
            self.clear_header('Content-Type')
            self.set_status(http.client.NO_CONTENT)
            return

        self.set_header("Content-Type", _CONTENT_TYPE_JSONAPI)
        response = entity
        if isinstance(entity, dict):
            response = {}
            response.update(entity)
            response["jsonapi"] = {
                "version": "1.0"
            }

        self.set_status(http.client.OK)
        self.write(escape.json_encode(response))
        self.flush()

    def _send_created_to_client(self, identifier):
        """Sends a created message to the client for a given resource

        """
        url = self.request.full_url()

        if identifier is not None:
            url = url_path_join(url, identifier)

        location = with_end_slash(url)

        self.set_status(http.client.CREATED.value)
        self.set_header("Location", location)
        self.clear_header('Content-Type')
        self.flush()
