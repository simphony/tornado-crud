import abc


class BaseRenderer(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def content_type(self):
        """
        Must return the content type of the
        generated representation, as a string.

        example: 'application/json'
        """

    @abc.abstractmethod
    def render(self, representation):
        """
        Converts a dictionary representation into
        the data to return as payload
        """
