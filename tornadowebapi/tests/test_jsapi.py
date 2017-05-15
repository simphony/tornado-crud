from collections import OrderedDict
from unittest import mock

from tornadowebapi.http import httpstatus
from tornadowebapi.registry import Registry
from tornadowebapi.tests.resource_handlers import (
     StudentModelConn, TeacherModelConn, FrobnicatorModelConn)
from tornadowebapi.tests.utils import AsyncHTTPTestCase
from tornado import web


class TestJSAPIHandler(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        StudentModelConn.collection = OrderedDict()
        StudentModelConn.id = 0

    def get_app(self):
        registry = Registry()
        registry.register(StudentModelConn)
        registry.register(TeacherModelConn)
        registry.register(FrobnicatorModelConn)
        handlers = registry.api_handlers('/')
        app = web.Application(handlers=handlers)
        app.hub = mock.Mock()
        return app

    def test_jsapi(self):
        res = self.fetch("/jsapi/v1/resources.js")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertIn(b'"Student" : new Resource("students")',
                      res.body)
        self.assertIn(b'"Teacher" : new Resource("teachers")',
                      res.body)
        self.assertIn(b'"Frobnicator" : new Resource("frobnicators")',
                      res.body)
