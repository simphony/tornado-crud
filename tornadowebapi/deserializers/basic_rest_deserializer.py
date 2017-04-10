from tornadowebapi.exceptions import BadRepresentation
from .base_deserializer import BaseDeserializer


class BasicRESTDeserializer(BaseDeserializer):
    """Deserializes data from our own flavor of REST data"""
    def deserialize_resource(self, resource_class, data):
        instance = resource_class()
        optional = []
        for trait_name, trait_class in instance.traits().items():
            if trait_class.metadata.get("optional") is True:
                optional.append(trait_name)

        for trait_name, trait_class in instance.traits().items():
            try:
                value = data[trait_name]
            except KeyError:
                if trait_name not in optional:
                    raise BadRepresentation(
                        message="Missing mandatory element: {}".format(
                            trait_name))
                else:
                    continue

            setattr(instance, trait_name, value)

        return instance
