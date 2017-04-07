import unittest

from tornadowebapi.transports.basic_rest_transport import BasicRESTTransport


class TestBasicRESTTransport(unittest.TestCase):
    def test_init(self):
        transport = BasicRESTTransport()
        self.assertIsNotNone(transport.renderer)
        self.assertIsNotNone(transport.parser)
        self.assertIsNotNone(transport.serializer)
        self.assertIsNotNone(transport.deserializer)
