from .base_deserializer import BaseDeserializer


class BasicRESTDeserializer(BaseDeserializer):
    """Deserializes data from our own flavor of REST data.
    Our flavor does not contain the identifier in the payload,
    so we have to rely on what is passed"""
    def deserialize_resource(self,
                             resource_class,
                             identifier,
                             data=None):
        instance = resource_class(identifier=identifier)

        if data is None:
            return instance

        for key, value in data.items():
            setattr(instance, key, value)

        return instance
