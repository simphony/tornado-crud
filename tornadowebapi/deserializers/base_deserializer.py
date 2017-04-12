import abc


class BaseDeserializer(metaclass=abc.ABCMeta):
    """Converts a dictionary of keys coming from
    the parser into an actual entity to pass to the
    resource handlers."""

    @abc.abstractmethod
    def deserialize_resource(self,
                             resource_class,
                             identifier,
                             data=None):
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
            Identifier can also be None.

        data: dict or None
            The data obtained from the parsing of the payload.
            If the data is None, the deserialization will produce an instance
            with only the identifier defined.

        Returns
        -------
        Resource
            An instance of the resource_class.
        """
