from unittest.mock import Mock

from tornado.testing import AsyncTestCase, gen_test
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.tests.resource_handlers import ServerInfoHandler, \
    TeacherHandler


class TestResourceHandler(AsyncTestCase):
    @gen_test
    def test_basic_expectations(self):
        handler = ResourceHandler(Mock(), Mock())
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
        handler = ResourceHandler(Mock(), Mock())

        with self.assertRaises(TypeError):
            ResourceHandler.bound_name()

        handler.resource_class = str
        with self.assertRaises(TypeError):
            ResourceHandler.bound_name()

        self.assertEqual(ServerInfoHandler.bound_name(), "serverinfo")
        self.assertEqual(TeacherHandler.bound_name(), "teachers")

    def test_handle_singleton(self):
        self.assertTrue(ServerInfoHandler.handles_singleton())
        self.assertFalse(TeacherHandler.handles_singleton())
