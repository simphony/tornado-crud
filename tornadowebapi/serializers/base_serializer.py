import abc


class BaseSerializer(metaclass=abc.ABCMeta):
    """The serializer is in charge of converting the data
    from the ResourceHandler into a dictionary with appropriate
    keys.

    This dictionary will then be passed to the renderer to be
    converted into something that is shown on the web.

    NOTE: These methods will eventually accept a model object, rather than
    the current parameters
    """
    @abc.abstractmethod
    def serialize_collection(self, collection_name, collection_items):
        """Serializes a collection of items"""

    @abc.abstractmethod
    def serialize_exception(self, exception_representation):
        """Serializes an exception with a given representation"""

    @abc.abstractmethod
    def serialize_resource(self, collection_name, identifier, representation):
        """Serializes a resource of a given collection name, identifier
        and given representation"""
