from .base_deserializer import BaseDeserializer


class BasicRESTDeserializer(BaseDeserializer):
    def deserialize_resource_data(self, data):
        return data
