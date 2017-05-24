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
    def create_object(self, instance, **kwargs):
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
    def retrieve_object(self, instance, **kwargs):
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
    def replace_object(self, instance, **kwargs):
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
    def update_object(self, instance, **kwargs):
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
    def delete_object(self, instance, **kwargs):
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
    def retrieve_collection(
            self, items_response, offset=None, limit=None, **kwargs):
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
