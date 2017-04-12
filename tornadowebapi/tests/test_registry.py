import unittest
from unittest import mock

from tornadowebapi.registry import Registry
from tornadowebapi.tests.resource_handlers import (
    StudentHandler, SheepHandler, OctopusHandler, FrobnicatorHandler,
    WrongClassHandler)
from tornadowebapi.transports.base_transport import BaseTransport


class TestRegistry(unittest.TestCase):
    def test_instantiation(self):
        reg = Registry()

        # Register the classes.
        reg.register(StudentHandler)
        reg.register(SheepHandler)
        reg.register(OctopusHandler)
        reg.register(FrobnicatorHandler)

        # Check if they are there with the appropriate form
        self.assertIn("students", reg)
        self.assertIn("sheep", reg)
        self.assertIn("octopi", reg)
        self.assertEqual(reg["students"], StudentHandler)
        self.assertEqual(reg["sheep"], SheepHandler)
        self.assertEqual(reg["octopi"], OctopusHandler)

        self.assertIn("frobnicators", reg)
        self.assertEqual(reg["frobnicators"], FrobnicatorHandler)

    def test_double_registration(self):
        reg = Registry()

        reg.register(StudentHandler)
        with self.assertRaises(ValueError):
            reg.register(StudentHandler)

    def test_incorrect_class_registration(self):
        reg = Registry()

        with self.assertRaises(TypeError):
            reg.register("hello")

        with self.assertRaises(TypeError):
            reg.register(int)

        with self.assertRaises(TypeError):
            reg.register(WrongClassHandler)

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
