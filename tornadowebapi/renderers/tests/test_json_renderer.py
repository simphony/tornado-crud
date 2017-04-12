import unittest

from tornadowebapi.renderers import JSONRenderer


class TestJSONRenderer(unittest.TestCase):
    def test_basic_rendering(self):
        renderer = JSONRenderer()
        self.assertEqual(renderer.render({}), "{}")
        self.assertEqual(renderer.render(None), None)
