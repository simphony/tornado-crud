from unittest.mock import Mock

from tornado.testing import AsyncTestCase, gen_test
from tornadowebapi.resource_handler import ResourceHandler


class TestResourceHandler(AsyncTestCase):
    @gen_test
    def test_basic_expectations(self):
        handler = ResourceHandler(Mock(), Mock())
        with self.assertRaises(NotImplementedError):
            yield handler.create(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.retrieve("")

        with self.assertRaises(NotImplementedError):
            yield handler.update(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.delete("")

        with self.assertRaises(NotImplementedError):
            yield handler.items(Mock())
