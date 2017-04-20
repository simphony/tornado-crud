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
    - scope
        string
        Expresses the scope of the trait information. If specified, it accepts
        either of the two values:

            - "input": the trait is only relevant for the input representation
              and will be parsed, according to the other metadata, only during
              input operations. During output, the trait will not be present
              in the resulting representation, if specified.
            - "output": the trait is only relevant for the output
              representation. If specified during an input operation, it will
              be ignored.
            - If unspecified, the trait will be validated and accepted in both
              directions.

        Typical uses of scopes are:

            - you want to specify "readonly" information in your resource
              that you are not able to modify, but the server can return
              anyway. Example: the state of an operation. In that case, use
              "output"

            - you want to specify information that the client can specify,
              but the server does not want to (or cannot) return anymore.


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
def mandatory_absents(resource, scope):
    """Returns a set of the trait names that are mandatory, but do not
    have a specified value (i.e. they are Absent).

    Parameters
    ----------
    resource: Resource or ResourceFragment
        The resource to check
    scope: str
        Valid values are "input" and "output". Perform the check as if the
        resource is primed for an input operation (e.g. coming in as a POST or
        PUT) or for an output one (e.g. a GET)
    """
    if scope not in ["input", "output"]:
        raise ValueError("Scope must be either input or output")

    res = set()
    for trait_name, trait in resource.traits().items():
        if trait.metadata.get("scope", scope) != scope:
            continue

        trait_optional = trait.metadata.get("optional", False)
        if getattr(resource, trait_name) == Absent and not trait_optional:
            res.add(trait_name)
        elif isinstance(trait, OneOf):
            res.update([
                ".".join([trait_name, x]) for x in mandatory_absents(
                    getattr(resource, trait_name), scope)])

    return res


def is_valid(resource, scope):
    """Returns True if the resource is valid, False otherwise.
    Validity is defined as follows:
        - identifier is not None
        - mandatory_absents is empty
    """
    return (resource.identifier is not None and
            len(mandatory_absents(resource, scope)) == 0)
