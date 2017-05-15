from tornadowebapi.base_resource import BaseSchema


class SchemaFragment(BaseSchema):
    """Represents a sub-resource that is not addressable with an identifier
    and is not part of a collection.

    Typically used to put some additional data into a resource,
    while keeping it as a separate class.
    Differently from resources, fragments don't have an identifier,
    and are not addressable.

    traitlets specifications directives of Resource are still valid.
    """
