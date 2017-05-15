import abc

from tornadowebapi.base_resource import BaseSchema
from tornadowebapi.exceptions import WebAPIException
from tornadowebapi.items_response import ItemsResponse


class BaseSerializer(metaclass=abc.ABCMeta):
    """The serializer is in charge of converting the data
    from the DataLayer into a dictionary with appropriate
    keys.

    This dictionary will then be passed to the renderer to be
    converted into something that is shown on the web.
    """
    def serialize(self, entity):
        """
        Serializes the passed entity. Returns a dictionary with the
        result of the serialization

        Parameters
        ----------
        entity: BaseSchema or ItemsResponse or WebAPIException

        Returns
        -------
        dict
            A dict representing the serialized entity
        """
        if isinstance(entity, BaseSchema):
            return self.serialize_resource(entity)
        elif isinstance(entity, ItemsResponse):
            return self.serialize_items_response(entity)
        elif isinstance(entity, WebAPIException):
            return self.serialize_exception(entity)
        else:
            raise TypeError("Unrecognized entity {} in "
                            "BaseSerializer.serialize".format(entity))

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
