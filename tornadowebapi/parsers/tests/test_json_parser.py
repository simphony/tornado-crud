import unittest

from tornadowebapi.parsers import JSONParser


class TestJSONParser(unittest.TestCase):
    def test_basic_functionality(self):
        parser = JSONParser()
        self.assertEqual(parser.parse("{}"), {})
        self.assertEqual(parser.parse(None), None)
