from tornado import gen, log
from tornadowebapi.schema import Schema
from tornadowebapi.singleton_schema import SingletonSchema

from . import exceptions


class ModelConnector:
    """Base class for model connectors.
    To implement a new ModelConnector class, inherit from this subclass
    and reimplement the CRUD class methods with the appropriate
    logic. Additionally, specify a resource_class of type Resource.

    The ModelConnector exports two member vars: application and current_user.
    They are equivalent to the members in the tornado web handler.
    """

    #: Specify the Resource subtype this handler manipulates.
    #: Must be overridden in the derived class.
    resource_class = None

    def __init__(self, application, current_user):
        """Initializes the Resource with a given application and user instance

        Parameters
        ----------
        application: web.Application
            The tornado web application
        current_user:
            The current user as passed by the underlying RequestHandler.
        """
        self.application = application
        self.current_user = current_user
        self.log = log.app_log

    @gen.coroutine
    def create(self, instance, **kwargs):
        """Called to create a resource with the given data.
        The member is passed with an instance of Resource, pre-filled
        with the data from the passed (and decoded) payload.
        This member should be responsible for storing or acting on the
        request, and finally setting the resource.identifier value.

        Correspond to a POST operation on the resource collection.

        Parameters
        ----------
        instance: Schema
            An instance of the associated resource_class, pre-filled
            with the data from the payload of the HTTP request.
            The identifier of this resource will be None, and it must be
            filled by the routine with a str value.

        Returns
        -------
        None

        Raises
        ------
        Exists:
            Raised when the resource cannot be created because of a
            conflicting already existing resource.
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def retrieve(self, instance, **kwargs):
        """Called to retrieve a specific resource given its
        identifier. Correspond to a GET operation on the resource URL.

        The method is called with an empty instance of the resource_class
        (except for the identifier). At the end of the method, it must have
        been filled with all the non-optional information.

        This routine returns nothing.

        Parameters
        ----------
        instance:
            An instance of the resource_class.
            This instance has only the identifier filled. The rest
            must be filled by this routine.

        Returns
        -------
        None

        Raises
        ------
        NotFound:
            Raised if the resource with the given identifier cannot
            be found
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def update(self, instance, **kwargs):
        """Called to update (fully) a specific Resource given its
        identifier with new data. Correspond to a PUT operation on the
        Resource URL.

        Parameters
        ----------
        instance:
            An instance of the resource_class. This instance will be filled
            with data from the payload.

        Returns
        -------
        None

        Raises
        ------
        NotFound:
            Raised if the resource with the given identifier cannot
            be found
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def delete(self, instance, **kwargs):
        """Called to delete a specific resource given its identifier.
        Corresponds to a DELETE operation on the resource URL.

        The passed i

        Parameters
        ----------
        instance:
            An instance of the Resource type. Only the identifier will
            be filled.

        Returns
        -------
        None

        Raises
        ------
        NotFound:
            Raised if the resource with the given identifier cannot be found
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def exists(self, instance, **kwargs):
        """Returns True if the resource with a given identifier
        exists. False otherwise.

        Parameters
        ----------
        instance: Schema
            A Resource instance. Only the identifier will be filled.

        Returns
        -------
        bool: True if found, False otherwise.
        """
        try:
            yield self.retrieve(instance)
        except exceptions.NotFound:
            return False

        return True

    @gen.coroutine
    def items(self, items_response, offset=None, limit=None, **kwargs):
        """Invoked when a request is performed to the collection
        URL. Passes an empty items_response object that must be filled
        with the relevant information.
        Corresponds to a GET operation on the collection URL.

        Parameters
        ----------
        items_response: ItemsResponse
            An ItemsResponse instance with the details of the sublist
            of presented items.
        offset: int or None
            The offset requested in as a query argument.
        limit: int or None
            The maximum amount of elements to return.

        Raises
        ------
        NotImplementedError:
            If the resource collection does not support the method.
        """
        raise NotImplementedError()

    def preprocess_representation(self, representation):
        """Hook that inserts after the parsing and before the deserializer.
        Gives a chance to manipulate the representation incoming from a
        request.
        Be aware that the concrete content of this representation depends on
        the transport type (specifically, the deserializer).

        If you change serializer/deserializer, the format passing through this
        method will be different and therefore its code may not be appropriate
        anymore. For this reason, any generic exception occurring in this
        method will be converted into a BadRepresentation exception.
        Exceptions that belong to this distribution will be let through to
        produce the expected response.

        By default, this method does nothing, accepts any representation,
        and returns the same representation.

        The method can also be used to modify the incoming representation
        so that it's compliant with the expectations, or return a new
        representation.

        Returns
        -------
        The representation that will be used.
        """
        return representation

    def preprocess_identifier(self, identifier):
        """Validates the identifier from a request.
        Any exception occurring in this method will be converted into
        a NotFound exception.
        Exceptions that belong to this distribution will be let through to
        produce the expected response.

        Note: We use NotFound (404) because the URL is likely valid.
        If our identifiers are all integers, so that

        /foo/1/

        is a valid URL for identifier 1, and the following url

        /foo/whatever/

        Is simply not present.

        This method is always called first in the request chain of methods
        accepting an identifier. By default, it does nothing,
        accepts any identifier, and returns the same identifier.

        The method can also be used to modify the incoming identifier
        so that it's compliant with the expectations, or return a new
        identifier.

        Returns
        -------
        The identifier that will be used.
        """
        return identifier

    @classmethod
    def handles_singleton(cls):
        """Returns true if the handler resource_class is a singleton class.
        Returns false otherwise."""
        resource_class = cls.resource_class

        if resource_class is None:
            raise TypeError(
                "resource_class for handler {} must not be None".format(
                    cls
                ))

        if issubclass(resource_class, Schema):
            return False
        elif issubclass(resource_class, SingletonSchema):
            return True

        raise TypeError(
            "resource_class for handler {} must be a "
            "subtype of BaseResource. Found {}".format(
                cls,
                resource_class))

    @classmethod
    def bound_name(cls):
        """Returns the name under which the resource will be presented as
        a URL /name/.
        This passes through the call to its name if singleton,
        or to the collection name if not.
        """
        resource_class = cls.resource_class
        if cls.handles_singleton():
            return resource_class.name()
        else:
            return resource_class.collection_name()
