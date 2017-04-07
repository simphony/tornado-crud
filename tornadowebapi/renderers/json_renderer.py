from tornado import escape

from .base_renderer import BaseRenderer


class JSONRenderer(BaseRenderer):
    def render(self, representation):
        return escape.json_encode(representation)
