from tornado import gen, log


class ModelConnector:
    """Base class for model connectors.
    To implement a new ModelConnector class, inherit from this subclass
    and reimplement the CRUD class methods with the appropriate
    logic.

    The ModelConnector exports two member vars: application and current_user.
    They are equivalent to the members in the tornado web handler.
    """

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
    def create_object(self, data, **kwargs):
        """Called to create a resource with the given data.
        The member is passed with an instance of Resource, pre-filled
        with the data from the passed (and decoded) payload.
        This member should be responsible for storing or acting on the
        request, and finally setting the resource.identifier value.

        Correspond to a POST operation on the resource collection.

        Parameters
        ----------
        data: dict
            A dict of the data submitted as payload, validated against the
            schema.

        Returns
        -------
        obj: the model object

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
    def retrieve_object(self, identifier, **kwargs):
        """Called to retrieve a specific resource given its
        identifier. Correspond to a GET operation on the resource URL.

        The method is called with an empty instance of the resource_class
        (except for the identifier). At the end of the method, it must have
        been filled with all the non-optional information.

        This routine returns nothing.

        Parameters
        ----------
        identifier:
            the identifier of the object

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
    def replace_object(self, identifier, data, **kwargs):
        """Called to update (fully) a specific Resource given its
        identifier with new data. Correspond to a PUT operation on the
        Resource URL.

        Parameters
        ----------
        identifier: str
            The identifier of the object to replace
        data: dict
            The validated dict of the data.

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
    def update_object(self, identifier, data, **kwargs):
        """Called to update (partially) a specific Resource given its
        identifier with new data. Correspond to a PATCH operation on the
        Resource URL.

        Parameters
        ----------
        identifier: str
            The identifier of the object to update.
        data: dict
            The validated dict of the data.

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
    def delete_object(self, identifier, **kwargs):
        """Called to delete a specific resource given its identifier.
        Corresponds to a DELETE operation on the resource URL.

        Parameters
        ----------
        identifier: str
            The identifier of the object to delete

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
    def retrieve_collection(
            self, offset=None, limit=None, **kwargs):
        """Invoked when a request is performed to the collection
        URL. Passes an empty items_response object that must be filled
        with the relevant information.
        Corresponds to a GET operation on the collection URL.

        Parameters
        ----------
        offset: int or None
            The offset requested in as a query argument.
        limit: int or None
            The maximum amount of elements to return.

        Returns
        -------
        items_response: ItemsResponse
            An ItemsResponse instance with the details of the sublist
            of presented items.

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
