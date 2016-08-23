from . import exceptions
from tornado import gen, log


class Resource:
    """Base class for REST resources.
    To implement a new Resource class, inherit from this subclass
    and reimplement the CRUD class methods with the appropriate
    logic.

    The Resource exports two member vars: application and current_user.
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
    def create(self, representation):
        """Called to create a resource with a given representation
        The representation is a dictionary containing keys. The
        reimplementing code is responsible for checking the validity
        of the representation. Correspond to a POST operation on the
        resource collection.

        Parameters
        ----------
        representation: dict
            A dictionary containing the representation as from the
            HTTP request.

        Returns
        -------
        id: str
            An identifier identifying the newly created resource.
            It must be unique within the collection.

        Raises
        ------
        UnprocessableRepresentation:
            Raised when the representation does not validate according
            to the resource expected representation.
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def retrieve(self, identifier):
        """Called to retrieve a specific resource given its
        identifier. Correspond to a GET operation on the resource URL.

        Parameters
        ----------
        identifier: str
            A string identifying the resource

        Returns
        -------
        representation: dict
            a dict representation of the resource.

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
    def update(self, identifier, representation):
        """Called to update a specific resource given its
        identifier with a new representation.
        The method is responsible for validating the representation
        content. Correspond to a PUT operation on the resource URL.

        Parameters
        ----------
        identifier: str
            A string identifying the resource
        representation: dict
            a dict representation of the resource.

        Returns
        -------
        None

        Raises
        ------
        NotFound:
            Raised if the resource with the given identifier cannot
            be found
        UnprocessableRepresentation:
            Raised when the representation does not validate according
            to the resource expected representation.
        NotImplementedError:
            If the resource does not support the method.
        """
        raise NotImplementedError()

    @gen.coroutine
    def delete(self, identifier):
        """Called to delete a specific resource given its identifier.
        Corresponds to a DELETE operation on the resource URL.

        Parameters
        ----------
        identifier: str
            A string identifying the resource

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
    def exists(self, identifier):
        """Returns True if the resource with a given identifier
        exists. False otherwise.

        Parameters
        ----------
        identifier: str
            A string identifying the resource

        Returns
        -------
        bool: True if found, False otherwise.
        """
        try:
            yield self.retrieve(identifier)
        except exceptions.NotFound:
            return False

        return True

    @gen.coroutine
    def items(self):
        """Invoked when a request is performed to the collection
        URL. Returns a list of identifiers available.
        Corresponds to a GET operation on the collection URL.

        Returns
        -------
        list: The list of available identifiers.

        Raises
        ------
        NotImplementedError:
            If the resource collection does not support the method.

        Notes
        -----
        For security reasons stemming from cross site execution,
        this list will not be rendered as a list in a json representation.
        Instead, a dictionary with the key "items" and value as this list
        will be returned.
        """
        return []
