from .base_deserializer import BaseDeserializer


class BasicRESTDeserializer(BaseDeserializer):
    """Deserializes data from our own flavor of REST data"""
    def deserialize_resource_data(self, data):
        return data
