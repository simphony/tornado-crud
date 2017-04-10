import unittest

from tornadowebapi.parsers import JSONParser
from tornadowebapi.renderers import JSONRenderer


class TestJSONParser(unittest.TestCase):
    def test_basic_functionality(self):
        parser = JSONParser()
        self.assertEqual(parser.parse("{}"), {})
        self.assertEqual(parser.parse(None), None)

    def test_parser_renderer(self):
        parser = JSONParser()
        renderer = JSONRenderer()

        for entity in [{}, None]:
            self.assertEqual(entity, parser.parse(renderer.render(entity)))
