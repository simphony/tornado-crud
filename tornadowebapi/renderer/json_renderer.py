from tornado import escape

from .base_renderer import BaseRenderer


class JSONRenderer(BaseRenderer):
    @property
    def content_type(self):
        return "application/json"

    def render(self, representation):
        return escape.json_encode(representation)
