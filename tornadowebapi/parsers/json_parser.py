from tornado import escape
from .base_parser import BaseParser


class JSONParser(BaseParser):
    """Parser is responsible for converting whatever
    is delievered as a payload into an appropriate
    internal representation that can continue.
    This representation is a dictionary"""

    @property
    def content_type(self):
        return "application/json"

    def parse(self, payload):
        return escape.json_decode(payload)
