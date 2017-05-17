from tornado import gen, web, template
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
        res_handler = self.get_model_connector()
        args = self.parsed_query_arguments()

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
    def post(self):
        res_handler = self.get_model_connector()
        args = self.parsed_query_arguments()

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
        res_handler = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("get",
                                     str(res_handler),
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        with self.exceptions_to_http("get", str(res_handler), identifier):
            resource = transport.deserializer.deserialize(
                res_handler.resource_class,
                identifier)

            self._check_none(identifier, "identifier", "preprocess_identifier")

            yield res_handler.retrieve(resource, **args)

            self._check_resource_sanity(resource, "output")

        self._send_to_client(resource)

    @gen.coroutine
    def post(self, identifier):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        res_handler = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("post",
                                     str(res_handler),
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        with self.exceptions_to_http("post", str(res_handler), identifier):
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
    def put(self, identifier):
        """Replaces the resource with a new representation."""
        res_handler = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("put",
                                     str(res_handler),
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        on_generic_raise = self.to_http_exception(
            exceptions.BadRepresentation(
                "Generic exception during preprocessing of {}".format(
                    str(res_handler))))
        with self.exceptions_to_http("put",
                                     str(res_handler),
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
                                     str(res_handler),
                                     identifier):
            self._check_resource_sanity(resource, "input")

            yield res_handler.update(resource, **args)

        self._send_to_client(None)

    @gen.coroutine
    def delete(self, identifier):
        """Deletes the resource."""
        res_handler = self.get_model_connector()
        transport = self._registry.transport
        args = self.parsed_query_arguments()

        with self.exceptions_to_http("delete",
                                     str(res_handler),
                                     identifier,
                                     on_generic_raise=web.HTTPError(
                                         httpstatus.NOT_FOUND)):
            identifier = res_handler.preprocess_identifier(identifier)

        self._check_none(identifier, "identifier", "preprocess_identifier")

        with self.exceptions_to_http("delete",
                                     str(res_handler),
                                     identifier):

            resource = transport.deserializer.deserialize(
                res_handler.resource_class,
                identifier)

            yield res_handler.delete(resource, **args)

        self._send_to_client(None)


class ResourceSingletonDetails(Resource):
    @gen.coroutine
    def get(self):
        res_handler = self.get_model_connector()
        args = self.parsed_query_arguments()

        transport = self._registry.transport

        with self.exceptions_to_http(res_handler, "get"):
            resource = transport.deserializer.deserialize(
                res_handler.resource_class)

            yield res_handler.retrieve(resource, **args)

            self._check_resource_sanity(resource, "output")

        self._send_to_client(resource)

    @gen.coroutine
    def post(self):
        res_handler = self.get_model_connector()
        args = self.parsed_query_arguments()

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
    def put(self):
        res_handler = self.get_model_connector()
        args = self.parsed_query_arguments()

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
    def delete(self):
        res_handler = self.get_model_connector()
        args = self.parsed_query_arguments()

        transport = self._registry.transport

        with self.exceptions_to_http(res_handler, "delete"):
            resource = transport.deserializer.deserialize(
                res_handler.resource_class)

            yield res_handler.delete(resource, **args)

        self._send_to_client(None)


class JSAPIWebHandler(Resource):
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
