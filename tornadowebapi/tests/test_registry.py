import unittest
from unittest import mock

from tornadowebapi.registry import Registry
from tornadowebapi.tests.resource_handlers import (
    StudentDetails, SheepDetails, OctopusDetails, FrobnicatorDetails)
from tornadowebapi.transports.base_transport import BaseTransport


class TestRegistry(unittest.TestCase):
    def test_instantiation(self):
        reg = Registry()

        # Register the classes.
        reg.register("/students/(.*)/", StudentDetails)
        reg.register("/sheep/(.*)/", SheepDetails)
        reg.register("/octopuses/(.*)/", OctopusDetails)
        reg.register("/frobnicators/(.*)/", FrobnicatorDetails)

        api_handlers = reg.api_handlers("/foo")
        self.assertEqual(len(api_handlers), 4)

    def test_double_registration(self):
        reg = Registry()

        reg.register("/students/(.*)/", StudentDetails)
        with self.assertRaises(ValueError):
            reg.register("/students/(.*)/", StudentDetails)

    def test_incorrect_class_registration(self):
        reg = Registry()

        with self.assertRaises(TypeError):
            reg.register("/students/(.*)/", "hello")

        with self.assertRaises(TypeError):
            reg.register("/students/(.*)/", int)

    def test_authenticator(self):
        reg = Registry()

        self.assertIsNotNone(reg.authenticator)

    def test_empty_api_handlers(self):
        reg = Registry()
        api_handlers = reg.api_handlers("/foo")
        self.assertEqual(len(api_handlers), 0)

    def test_transport(self):
        reg = Registry()
        self.assertIsInstance(reg.transport, BaseTransport)

        mock_transport = mock.Mock(spec=BaseTransport)
        reg = Registry(transport=mock_transport)
        self.assertEqual(reg.transport, mock_transport)
