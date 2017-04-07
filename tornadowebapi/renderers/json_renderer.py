from tornado import escape

from .base_renderer import BaseRenderer


class JSONRenderer(BaseRenderer):
    def render(self, representation):
        if representation is not None:
            return escape.json_encode(representation)

        return None
