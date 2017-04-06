import abc


class BaseDeserializer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def deserialize_resource_data(self, data):
        pass
