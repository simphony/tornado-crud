from tornadowebapi.resource import Resource
from tornadowebapi.traitlets import OneOf
from .base_deserializer import BaseDeserializer


class BasicRESTDeserializer(BaseDeserializer):
    """Deserializes data from our own flavor of REST data.
    Our flavor does not contain the identifier in the payload,
    so we have to rely on what is passed"""
    def deserialize_resource(self,
                             resource_class,
                             identifier=None,
                             data=None):
        if identifier is None:
            if issubclass(resource_class, Resource):
                raise ValueError("Identifier must not be none for a "
                                 "Resource class")
            resource = resource_class()
        else:
            resource = resource_class(identifier=identifier)

        if data is None:
            return resource

        for trait_name, trait in resource.traits().items():
            if trait_name not in data:
                continue

            if isinstance(trait, OneOf):
                fragment_class = trait.klass
                setattr(resource,
                        trait_name,
                        self.deserialize_resource(
                            fragment_class,
                            None,
                            data[trait_name]))
            else:
                setattr(resource, trait_name, data[trait_name])

        return resource
