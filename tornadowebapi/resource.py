from tornadowebapi.traitlets import HasTraits


class Resource(HasTraits):
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
