from unittest.mock import Mock

from tornado.testing import AsyncTestCase, gen_test
from tornadowebapi.model_connector import ModelConnector


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
