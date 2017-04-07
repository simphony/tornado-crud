import abc


class BaseParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse(self, payload):
        """Parses the payload and returns a dictionary"""
