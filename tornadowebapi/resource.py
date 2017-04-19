from tornadowebapi.base_resource import BaseResource
from tornadowebapi.traitlets import Absent, OneOf


class Resource(BaseResource):
    """A model representing a resource in our system.
    Must be reimplemented for the specific resource in our domain,
    as well as specifying its properties with traitlets.

    The following metadata in the specified traitlets are accepted:

    - optional
        bool, default False.
        If True, the information can be omitted from the representation
        when creating.
        If False, the information must be present, or an error
        BadRepresentation will be raised.

    The resource is always identified via its collection name, and
    its identifier. Both will end up in the URL, like so

    /collection_name/identifier/

    """
    def __init__(self, identifier, *args, **kwargs):
        self.identifier = identifier

        super(Resource, self).__init__(*args, **kwargs)

    @classmethod
    def collection_name(cls):
        """Identifies the name of the collection. By REST convention, it is
        a plural form of the class name, so the default is the name of the
        class, lowercase, and with an "s" added at the end.

        Override this method to return a better pluralization.
        """
        return cls.__name__.lower() + "s"

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        if not (value is None or isinstance(value, str)):
            raise ValueError("Identifier must be a string. Got {}".format(
                type(value)
            ))

        self._identifier = value


# Not as members because we want to prevent collisions with actual
# resource subclass traits.
def mandatory_absents(resource):
    """Returns a set of the trait names that are mandatory, but do not
    have a specified value (i.e. they are Absent)."""
    res = set()
    for trait_name, trait_class in resource.traits().items():
        if (getattr(resource, trait_name) == Absent and not
                trait_class.metadata.get("optional", False)):
            res.add(trait_name)
        elif isinstance(trait_class, OneOf):
            res.update([
                ".".join([trait_name, x]) for x in mandatory_absents(
                    getattr(resource, trait_name))])

    return res


def is_valid(resource):
    """Returns True if the resource is valid, False otherwise.
    Validity is defined as follows:
        - identifier is not None
        - mandatory_absents is empty
    """
    return (resource.identifier is not None and
            len(mandatory_absents(resource)) == 0)
