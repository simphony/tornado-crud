import abc


class BaseSerializer(metaclass=abc.ABCMeta):
    """The serializer is in charge of converting the data
    from the ResourceHandler into a dictionary with appropriate
    keys.

    This dictionary will then be passed to the renderer to be
    converted into something that is shown on the web.
    """
    @abc.abstractmethod
    def serialize_items_response(self, items_response):
        """Serializes a collection of items.

        Parameters
        ----------
        items_response: ItemsResponse
            The ItemsResponse to serialize.

        Returns
        -------
        dict
            A dictionary containing the serialized version of the ItemsResponse
        """

    @abc.abstractmethod
    def serialize_exception(self, exception):
        """Given a WebAPIException occurred during the processing of a request,
        this method produces a serialization of the exception to be carried as
        payload in the error response.

        Parameters
        ----------
        exception: WebAPIException
            The exception to serialize

        Returns
        -------
        dict
            A dict representing the exception
        """

    @abc.abstractmethod
    def serialize_resource(self, resource):
        """Serializes a resource.

        Parameters
        ----------
        resource: Resource
            The resource to serialize

        Returns
        -------
        dict
            A dict representing the resource.
        """
