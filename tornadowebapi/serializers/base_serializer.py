import abc


class BaseSerializer(metaclass=abc.ABCMeta):
    """The serializer is in charge of converting the data
    from the ResourceHandler into a dictionary with appropriate
    keys.

    This dictionary will then be passed to the renderer to be
    converted into something that is shown on the web.
    """
    @abc.abstractmethod
    def serialize_collection(self, collection_name, collection_items):
        pass

    @abc.abstractmethod
    def serialize_exception(self, exception_representiation):
        pass

    @abc.abstractmethod
    def serialize_resource(self,
                           collection_name,
                           identifier,
                           resource_representation):
        pass
