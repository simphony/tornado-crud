from tornado import gen, log

from . import exceptions


class ResourceHandler:
    """Base class for resources.
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
        Exists:
            Raised when the resource cannot be created because of a
            conflicting already existing resource.
        BadRepresentation:
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
        BadRepresentation:
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
            Raised if the resource with the given identifier cannot be found
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

    def validate_representation(self, representation):
        """Validates the representation incoming from a request,
        after it has been decoded.
        Any generic exception occurring in this method will be
        converted into a BadRepresentation exception.
        Exceptions that belong to this distribution will be let through to
        produce the expected response.

        This method is always called before being dispatched to the CRUD
        methods accepting a representation. By default, it does nothing,
        accepts any representation, and returns the same representation.

        The method can also be used to modify the incoming representation
        so that it's compliant with the expectations, or return a new
        representation.

        Returns
        -------
        The representation that will be used.
        """
        return representation

    def validate_identifier(self, identifier):
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

        This method is always called before being dispatched to the CRUD
        methods accepting an identifier. By default, it does nothing,
        accepts any identifier, and returns the same identifier.

        The method can also be used to modify the incoming identifier
        so that it's compliant with the expectations, or return a new
        identifier.

        Returns
        -------
        The identifier that will be used.
        """
        return identifier
