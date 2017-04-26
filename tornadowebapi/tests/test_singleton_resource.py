import unittest

from tornadowebapi.tests.resource_handlers import ServerInfo


class TestSingletonResource(unittest.TestCase):
    def test_instantiation(self):
        s = ServerInfo()
        self.assertEqual(s.name(), "serverinfo")
