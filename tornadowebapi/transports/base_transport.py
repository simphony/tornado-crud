import abc


class BaseTransport(metaclass=abc.ABCMeta):
    """Base class for the REST transports, that is, the combined
    effort that goes in carrying data from its textual representation
    to its object representation."""
    parser = None
    renderer = None
    serializer = None
    deserializer = None

    @abc.abstractproperty
    def content_type(self):
        """Must return the appropriate content type for the transport.
        For example, a plain JSON can be application/json, but
        a JSON API must be "application/vnd.api+json"
        """
