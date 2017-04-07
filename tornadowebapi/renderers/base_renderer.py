import abc


class BaseRenderer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def render(self, representation):
        """
        Converts a dictionary representation into
        the data to return as payload
        """
