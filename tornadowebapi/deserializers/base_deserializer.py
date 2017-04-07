import abc


class BaseDeserializer(metaclass=abc.ABCMeta):
    """Converts a dictionary of keys coming from
    the parser into an actual entity to pass to the
    resource handlers."""

    @abc.abstractmethod
    def deserialize_resource_data(self, data):
        """Deserializes the incoming data and return something that
        the resource handler can accept"""
