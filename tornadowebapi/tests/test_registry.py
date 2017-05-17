import unittest
from unittest import mock

from tornadowebapi.registry import Registry
from tornadowebapi.tests.resource_handlers import (
    StudentModelConn, SheepModelConn, OctopusModelConn, FrobnicatorModelConn,
    WrongClassModelConn)
from tornadowebapi.transports.base_transport import BaseTransport


class TestRegistry(unittest.TestCase):
    def test_instantiation(self):
        reg = Registry()

        # Register the classes.
        reg.register(StudentModelConn)
        reg.register(SheepModelConn)
        reg.register(OctopusModelConn)
        reg.register(FrobnicatorModelConn)

        api_handlers = reg.api_handlers("/foo")
        self.assertEqual(len(api_handlers), 9)

        # Check if they are there with the appropriate form
        self.assertIn("students", reg)
        self.assertIn("sheep", reg)
        self.assertIn("octopi", reg)
        self.assertEqual(reg["students"], StudentModelConn)
        self.assertEqual(reg["sheep"], SheepModelConn)
        self.assertEqual(reg["octopi"], OctopusModelConn)

        self.assertIn("frobnicators", reg)
        self.assertEqual(reg["frobnicators"], FrobnicatorModelConn)

    def test_double_registration(self):
        reg = Registry()

        reg.register(StudentModelConn)
        with self.assertRaises(ValueError):
            reg.register(StudentModelConn)

    def test_incorrect_class_registration(self):
        reg = Registry()

        with self.assertRaises(TypeError):
            reg.register("hello")

        with self.assertRaises(TypeError):
            reg.register(int)

        with self.assertRaises(TypeError):
            reg.register(WrongClassModelConn)

    def test_authenticator(self):
        reg = Registry()

        self.assertIsNotNone(reg.authenticator)

    def test_api_handlers(self):
        reg = Registry()
        api_handlers = reg.api_handlers("/foo")
        self.assertEqual(len(api_handlers), 1)

        self.assertEqual(api_handlers[0][2]["registry"], reg)

    def test_transport(self):
        reg = Registry()
        self.assertIsInstance(reg.transport, BaseTransport)

        mock_transport = mock.Mock(spec=BaseTransport)
        reg = Registry(transport=mock_transport)
        self.assertEqual(reg.transport, mock_transport)
