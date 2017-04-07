import unittest
from unittest import mock

from tornadowebapi.registry import Registry
from tornadowebapi.tests.resources import Student, Sheep, Octopus
from tornadowebapi.transports.base_transport import BaseTransport


class TestRegistry(unittest.TestCase):
    def test_instantiation(self):
        reg = Registry()

        # Register the classes.
        reg.register(Student)
        reg.register(Sheep)
        reg.register(Octopus, "octopuses")

        # Check if they are there with the appropriate form
        self.assertIn("students", reg)
        self.assertIn("sheep", reg)
        self.assertIn("octopuses", reg)
        self.assertEqual(reg["students"], Student)
        self.assertEqual(reg["sheep"], Sheep)
        self.assertEqual(reg["octopuses"], Octopus)

    def test_authenticator(self):
        reg = Registry()

        self.assertIsNotNone(reg.authenticator)

    def test_api_handlers(self):
        reg = Registry()
        api_handlers = reg.api_handlers("/foo")
        self.assertEqual(len(api_handlers), 3)

        self.assertEqual(api_handlers[0][2]["registry"], reg)
        self.assertEqual(api_handlers[1][2]["registry"], reg)

    def test_transport(self):
        reg = Registry()
        self.assertIsInstance(reg.transport, BaseTransport)

        mock_transport = mock.Mock(spec=BaseTransport)
        reg = Registry(transport=mock_transport)
        self.assertEqual(reg.transport, mock_transport)
