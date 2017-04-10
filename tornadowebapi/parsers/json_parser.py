from tornado import escape
from tornadowebapi.exceptions import BadRepresentation
from .base_parser import BaseParser


class JSONParser(BaseParser):
    def parse(self, payload):
        if payload is None:
            return None

        try:
            return escape.json_decode(payload)
        except Exception:
            raise BadRepresentation()
