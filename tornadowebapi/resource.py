import http.client

from marshmallow import ValidationError
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from tornado import web, gen, escape
from tornado.log import app_log
from tornado.web import HTTPError
from tornadowebapi import exceptions
from tornadowebapi.errors import jsonapi_errors
from tornadowebapi.pagination import add_pagination_links
from tornadowebapi.schema import compute_schema
from tornadowebapi.utils import with_end_slash, url_path_join
from .querystring import QueryStringManager as QSManager

_CONTENT_TYPE_JSONAPI = 'application/vnd.api+json'


class Resource(web.RequestHandler):
    model_connector = None
    schema = None

    def initialize(self, registry, base_urlpath):
        """Initialization method for when the class is instantiated."""
        self._registry = registry
        self._base_urlpath = base_urlpath

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
            self.set_status(exc.status)
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


class ResourceList(Resource):
    """Handler for URLs without an identifier.
    """
    @gen.coroutine
    def get(self):
        connector = self.get_model_connector()
        qs = QSManager(self.request.query_arguments, self.schema)

        items, total_num = yield connector.retrieve_collection(qs)

        schema = compute_schema(self.schema,
                                {"many": True},
                                qs,
                                qs.include)
        result = schema.dump(items).data
        add_pagination_links(result, total_num, qs, "FIXME")

        self._send_to_client(result)

    @gen.coroutine
    def post(self):
        connector = self.get_model_connector()
        qs = QSManager(self.request.query_arguments, self.schema)

        json_data = escape.json_decode(self.request.body)

        schema = compute_schema(self.schema,
                                {},
                                qs,
                                qs.include)
        try:
            data, errors = schema.load(json_data)
        except IncorrectTypeError as e:
            errors = e.messages
            for error in errors['errors']:
                error['status'] = '409'
                error['title'] = "Incorrect type"
            raise exceptions.InvalidType({}, "")
        except ValidationError as e:
            errors = e.messages
            for message in errors['errors']:
                message['status'] = '422'
                message['title'] = "Validation error"
            raise exceptions.BadRequest({}, "")

        if errors:
            raise exceptions.BadRequest({}, "")

        identifier = yield connector.create_object(data)

        self._send_created_to_client(identifier)

    @gen.coroutine
    def put(self):
        """You cannot PUT on a collection"""
        raise HTTPError(http.client.METHOD_NOT_ALLOWED.value)

    @gen.coroutine
    def delete(self):
        raise HTTPError(http.client.METHOD_NOT_ALLOWED.value)


class ResourceDetails(Resource):
    pass


class ResourceSingletonDetails(Resource):
    pass

'''
class ResourceDetails(Resource):
    """Handler for URLs addressing a resource.
    """
    @gen.coroutine
    def get(self, identifier):
        """Retrieves the resource representation."""
        connector = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("get", str(connector), identifier):
            resource = transport.deserializer.deserialize(
                self.schema,
                identifier)

            self._check_none(identifier, "identifier", "preprocess_identifier")

            yield connector.retrieve_object(resource, **args)

            self._check_resource_sanity(resource, "output")

        self._send_to_client(resource)

    @gen.coroutine
    def post(self, identifier):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        connector = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("post", str(connector), identifier):
            resource = transport.deserializer.deserialize(
                self.schema,
                identifier)

        with self.exceptions_to_http("post", str(connector), identifier):
            try:
                yield connector.retrieve_object(resource, **args)
            except NotFound:
                raise web.HTTPError(httpstatus.NOT_FOUND)
            else:
                raise web.HTTPError(httpstatus.CONFLICT)

    @gen.coroutine
    def put(self, identifier):
        """Replaces the resource with a new representation."""
        connector = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation(
                "Generic exception during preprocessing of {}".format(
                    str(connector))))
        with self.exceptions_to_http("put",
                                     str(connector),
                                     identifier,
                                     on_generic_raise=on_generic_raise):
            try:
                resource = transport.deserializer.deserialize(
                    self.schema,
                    identifier,
                    transport.parser.parse(self.request.body))
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_none(resource,
                             "representation",
                             "preprocess_representation")

        with self.exceptions_to_http("put",
                                     str(connector),
                                     identifier):
            self._check_resource_sanity(resource, "input")

            yield connector.replace_object(resource, **args)

        self._send_to_client(None)

    @gen.coroutine
    def delete(self, identifier):
        """Deletes the resource."""
        connector = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("delete",
                                     str(connector),
                                     identifier):

            resource = transport.deserializer.deserialize(
                self.schema,
                identifier)

            yield connector.delete_object(resource, **args)

        self._send_to_client(None)


class ResourceSingletonDetails(Resource):
    @gen.coroutine
    def get(self):
        connector = self.get_model_connector()
        args = self.parsed_query_arguments()

        transport = self._registry.transport

        with self.exceptions_to_http(connector, "get"):
            resource = transport.deserializer.deserialize(
                self.schema)

            yield connector.retrieve_object(resource, **args)

            self._check_resource_sanity(resource, "output")

        self._send_to_client(resource)

    @gen.coroutine
    def post(self):
        connector = self.get_model_connector()
        args = self.parsed_query_arguments()

        transport = self._registry.transport
        payload = self.request.body

        with self.exceptions_to_http(connector, "post"):
            representation = transport.parser.parse(payload)
            try:
                resource = transport.deserializer.deserialize(
                    self.schema,
                    None,
                    representation,
                )
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_resource_sanity(resource, "input")

            try:
                yield connector.retrieve_object(resource)
            except NotFound:
                yield connector.create_object(resource, **args)
            else:
                raise exceptions.Exists()

        self._send_created_to_client(resource)

    @gen.coroutine
    def put(self):
        connector = self.get_model_connector()
        args = self.parsed_query_arguments()

        transport = self._registry.transport

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation("Generic exception during "
                                         "deserialization"))
        with self.exceptions_to_http(connector,
                                     "put",
                                     on_generic_raise=on_generic_raise):
            try:
                resource = transport.deserializer.deserialize(
                    self.schema,
                    None,
                    transport.parser.parse(self.request.body))
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_none(resource,
                             "representation",
                             "deserialize")

        with self.exceptions_to_http(connector, "put"):
            self._check_resource_sanity(resource, "input")

            yield connector.replace_object(resource, **args)

        self._send_to_client(None)

    @gen.coroutine
    def delete(self):
        connector = self.get_model_connector()
        args = self.parsed_query_arguments()

        transport = self._registry.transport

        with self.exceptions_to_http(connector, "delete"):
            resource = transport.deserializer.deserialize(
                self.schema)

            yield connector.delete_object(resource, **args)

        self._send_to_client(None)
        '''
