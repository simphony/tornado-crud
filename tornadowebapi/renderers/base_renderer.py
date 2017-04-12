import abc


class BaseRenderer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def render(self, representation):
        """
        Converts a dictionary representation into the data to return as
        payload. Different Renderers can output different payloads.
        For example, a JSON renderer can render JSON data, and a XML renderer
        can render XML data.

        Parameters
        ----------
        representation: dict or None
            A dictionary containing the low level representation we want to
            output. The renderer must be able to handle nested content.
            The renderer must be able to deal with the None representation
            gracefully.

        Returns
        -------
        string or None
            If there is a rendered representation for the passed dict
            representation, it returns it.
            It can return None when the passed representation produces no
            payload. Typically this happens when representation is None.
        """
