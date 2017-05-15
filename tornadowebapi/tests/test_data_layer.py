from unittest.mock import Mock

from tornado.testing import AsyncTestCase, gen_test
from tornadowebapi.model_connector import ModelConnector
from tornadowebapi.tests.resource_handlers import ServerInfoModelConn, \
    TeacherModelConn


class TestModelConn(AsyncTestCase):
    @gen_test
    def test_basic_expectations(self):
        handler = ModelConnector(Mock(), Mock())
        with self.assertRaises(NotImplementedError):
            yield handler.create(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.retrieve(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.update(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.delete(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.items(Mock())

    def test_bound_name(self):
        handler = ModelConnector(Mock(), Mock())

        with self.assertRaises(TypeError):
            ModelConnector.bound_name()

        handler.resource_class = str
        with self.assertRaises(TypeError):
            ModelConnector.bound_name()

        self.assertEqual(ServerInfoModelConn.bound_name(), "serverinfo")
        self.assertEqual(TeacherModelConn.bound_name(), "teachers")

    def test_handle_singleton(self):
        self.assertTrue(ServerInfoModelConn.handles_singleton())
        self.assertFalse(TeacherModelConn.handles_singleton())
