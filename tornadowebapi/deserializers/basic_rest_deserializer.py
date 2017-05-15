from tornadowebapi.schema import Schema
from tornadowebapi.schema_fragment import SchemaFragment
from tornadowebapi.singleton_resource import SingletonResource
from tornadowebapi.traitlets import OneOf
from .base_deserializer import BaseDeserializer


class BasicRESTDeserializer(BaseDeserializer):
    """Deserializes data from our own flavor of REST data.
    Our flavor does not contain the identifier in the payload,
    so we have to rely on what is passed"""
    def deserialize(self,
                    resource_class,
                    identifier=None,
                    data=None):

        if issubclass(resource_class, Schema):
            resource = resource_class(identifier=identifier)
        elif issubclass(resource_class, (SchemaFragment, SingletonResource)):
            resource = resource_class()
        else:
            raise TypeError(
                "Resource class is not a Resource or ResourceFragment"
            )

        if data is None:
            return resource

        for trait_name, trait in resource.traits().items():
            if trait_name not in data:
                continue

            if isinstance(trait, OneOf):
                fragment_class = trait.klass
                setattr(resource,
                        trait_name,
                        self.deserialize(
                            fragment_class,
                            None,
                            data[trait_name]))
            else:
                setattr(resource, trait_name, data[trait_name])

        return resource
