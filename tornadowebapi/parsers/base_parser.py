import abc


class BaseParser(metaclass=abc.ABCMeta):
    """The parser is responsible for converting whatever is delivered as a
    payload into an appropriate internal representation that can continue.
    This representation is a dictionary, or None if the payload was None.
    """
    @abc.abstractmethod
    def parse(self, payload):
        """Parses the payload, and returns a dictionary with the appropriate
        schema.

        Parameters
        ----------
        payload: string or None
            The payload coming from the HTTP request. Can be None if there
            is no payload

        Returns
        -------
        dict or None
            The dictionary extracted from the payload. If the payload is None,
            the result is None.
        """
