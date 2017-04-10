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
    def serialize_items_response(self, items_response):
        """Serializes a collection of items

        Parameters
        ----------
        items_response: ItemsResponse



        """

    @abc.abstractmethod
    def serialize_exception(self, exception):
        """Serializes an exception"""

    @abc.abstractmethod
    def serialize_resource(self, resource):
        """Serializes a resource"""
