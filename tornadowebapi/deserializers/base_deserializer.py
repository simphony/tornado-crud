import abc


class BaseDeserializer(metaclass=abc.ABCMeta):
    """Converts a dictionary of keys coming from
    the parser into an actual entity to pass to the
    resource handlers."""

    @abc.abstractmethod
    def deserialize_resource(self,
                             resource_class,
                             identifier,
                             data,
                             enforce_mandatory):
        """Deserializes the incoming data and return something that
        the resource handler can accept

        Parameters
        ----------
        resource_class:
            The class of the resource to deserialize

        identifier: string or None
            The identifier of the requested resource. This can also be
            present in the data, so particular care must be taken to check
            if they are equal.
            Identifier can also be None

        data: dict
            The data obtained from the parsing of the payload

        enforce_mandatory: bool
            If True, when the resource is instantiated, the mandatory
            traitlets will be enforced to be presend.
            If False, there will be no enforcement. This is set when a
            PATCH operation is requested.

        Returns
        -------
        Resource
            An instance of the resource_class.
        """
