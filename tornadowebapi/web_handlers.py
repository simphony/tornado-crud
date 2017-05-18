from tornado import gen, web
from tornado.web import HTTPError
from tornadowebapi.resource import Resource
from tornadowebapi.traitlets import TraitError
from . import exceptions
from .http import httpstatus
from .items_response import ItemsResponse


class ResourceList(Resource):
    """Handler for URLs without an identifier.
    """
    @gen.coroutine
    def get(self):
        connector = self.get_model_connector()
        args = self.parsed_query_arguments()

        items_response = ItemsResponse(self.schema)

        with self.exceptions_to_http(connector, "get"):
            yield connector.items(items_response, **args)

        for resource in items_response.items:
            self._check_none(resource.identifier,
                             "identifier",
                             "items")
            self._check_resource_sanity(resource, "output")

        self._send_to_client(items_response)

    @gen.coroutine
    def post(self):
        connector = self.get_model_connector()
        args = self.parsed_query_arguments()

        transport = self._registry.transport
        payload = self.request.body

        with self.exceptions_to_http(connector, "post"):
            representation = transport.parser.parse(payload)

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation("Generic exception "
                                         "during preprocessing"))

        with self.exceptions_to_http(connector, "post",
                                     on_generic_raise=on_generic_raise):
            representation = connector.preprocess_representation(
                representation)

            self._check_none(representation,
                             "representation",
                             "preprocess_representation")

        with self.exceptions_to_http(connector, "post"):
            try:
                resource = transport.deserializer.deserialize(
                    self.schema,
                    None,
                    representation,
                )
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_resource_sanity(resource, "input")

            yield connector.create(resource, **args)

            self._check_none(resource.identifier,
                             "resource_id",
                             "create()")

        self._send_created_to_client(resource)

    @gen.coroutine
    def put(self):
        """You cannot PUT on a collection"""
        raise HTTPError(httpstatus.METHOD_NOT_ALLOWED)

    @gen.coroutine
    def delete(self):
        raise HTTPError(httpstatus.METHOD_NOT_ALLOWED)


class ResourceDetails(Resource):
    """Handler for URLs addressing a resource.
    """
    @gen.coroutine
    def get(self, identifier):
        """Retrieves the resource representation."""
        connector = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("get",
                                     str(connector),
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = connector.preprocess_identifier(identifier)

        with self.exceptions_to_http("get", str(connector), identifier):
            resource = transport.deserializer.deserialize(
                self.schema,
                identifier)

            self._check_none(identifier, "identifier", "preprocess_identifier")

            yield connector.retrieve(resource, **args)

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

        with self.exceptions_to_http("post",
                                     str(connector),
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = connector.preprocess_identifier(identifier)

        with self.exceptions_to_http("post", str(connector), identifier):
            self._check_none(identifier, "identifier", "preprocess_identifier")

            resource = transport.deserializer.deserialize(
                self.schema,
                identifier)

            exists = yield connector.exists(resource, **args)

        if exists:
            raise web.HTTPError(httpstatus.CONFLICT)
        else:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    @gen.coroutine
    def put(self, identifier):
        """Replaces the resource with a new representation."""
        connector = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("put",
                                     str(connector),
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = connector.preprocess_identifier(identifier)

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation(
                "Generic exception during preprocessing of {}".format(
                    str(connector))))
        with self.exceptions_to_http("put",
                                     str(connector),
                                     identifier,
                                     on_generic_raise=on_generic_raise):
            self._check_none(identifier, "identifier", "preprocess_identifier")

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

            yield connector.update(resource, **args)

        self._send_to_client(None)

    @gen.coroutine
    def delete(self, identifier):
        """Deletes the resource."""
        connector = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("delete",
                                     str(connector),
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = connector.preprocess_identifier(identifier)

        self._check_none(identifier, "identifier", "preprocess_identifier")

        with self.exceptions_to_http("delete",
                                     str(connector),
                                     identifier):

            resource = transport.deserializer.deserialize(
                self.schema,
                identifier)

            yield connector.delete(resource, **args)

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

            yield connector.retrieve(resource, **args)

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

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation("Generic exception "
                                         "during preprocessing"))

        with self.exceptions_to_http(connector, "post",
                                     on_generic_raise=on_generic_raise):
            representation = connector.preprocess_representation(
                representation)

            self._check_none(representation,
                             "representation",
                             "preprocess_representation")

        with self.exceptions_to_http(connector, "post"):
            try:
                resource = transport.deserializer.deserialize(
                    self.schema,
                    None,
                    representation,
                )
            except TraitError as e:
                raise exceptions.BadRepresentation(message=str(e))

            self._check_resource_sanity(resource, "input")

            exists = yield connector.exists(resource)

            if exists:
                raise exceptions.Exists()

            yield connector.create(resource, **args)

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

            yield connector.update(resource, **args)

        self._send_to_client(None)

    @gen.coroutine
    def delete(self):
        connector = self.get_model_connector()
        args = self.parsed_query_arguments()

        transport = self._registry.transport

        with self.exceptions_to_http(connector, "delete"):
            resource = transport.deserializer.deserialize(
                self.schema)

            yield connector.delete(resource, **args)

        self._send_to_client(None)
