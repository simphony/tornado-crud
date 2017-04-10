from tornado import escape
from .base_parser import BaseParser


class JSONParser(BaseParser):

    def parse(self, payload):
        if payload is None:
            return None

        return escape.json_decode(payload)
