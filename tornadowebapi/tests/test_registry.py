import unittest
from unittest import mock

from tornadowebapi.registry import Registry
from tornadowebapi.tests.resource_handlers import (
    StudentHandler, SheepHandler, OctopusHandler, Frobnicator)
from tornadowebapi.transports.base_transport import BaseTransport


class TestRegistry(unittest.TestCase):
    def test_instantiation(self):
        reg = Registry()

        # Register the classes.
        reg.register(StudentHandler)
        reg.register(SheepHandler)
        reg.register(OctopusHandler, "octopuses")

        # Check if they are there with the appropriate form
        self.assertIn("students", reg)
        self.assertIn("sheep", reg)
        self.assertIn("octopuses", reg)
        self.assertEqual(reg["students"], StudentHandler)
        self.assertEqual(reg["sheep"], SheepHandler)
        self.assertEqual(reg["octopuses"], OctopusHandler)

    def test_strange_handler_name(self):
        reg = Registry()

        reg.register(Frobnicator)
        self.assertIn("frobnicators", reg)
        self.assertEqual(reg["frobnicators"], Frobnicator)

    def test_incorrect_class_registration(self):
        reg = Registry()

        with self.assertRaises(TypeError):
            reg.register("hello")

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
