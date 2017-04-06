import abc


class BaseSerializer(metaclass=abc.ABCMeta):
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
