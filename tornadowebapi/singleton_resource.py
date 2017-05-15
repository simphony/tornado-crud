from tornadowebapi.base_resource import BaseSchema


class SingletonResource(BaseSchema):
    """
    A model representing a singleton resource in our system, that is
    a resource that exists only as a single entity.
    As a result, the behavior is different from a collection-based resource:
    - There is only one resource
    - There is no concept of collection, nor of collection name
    - The resource has a name, which is the one that will end up in
    the url
    - The resource has no id.

    The URL will appear as

    /name/

    Regular Resource documentation applies for the definition.
    """
    @classmethod
    def name(cls):
        """
        Identifies the name of the resource.
        The default is the name of the class, lowercase.

        Override this method to return a different name.
        """
        return cls.__name__.lower()
