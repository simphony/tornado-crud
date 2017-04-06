import abc


class BaseParser(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def content_type(self):
        """
        Must return the content type of the
        understood representation, as a string.

        example: 'application/json'
        """

    def parse(self, payload):
        """Parses the payload and returns a dictionary"""
