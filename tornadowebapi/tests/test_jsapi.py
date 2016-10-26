from collections import OrderedDict
from unittest import mock

from tornadowebapi.http import httpstatus
from tornadowebapi.registry import Registry
from tornadowebapi.resource import Resource
from tornadowebapi.tests.utils import AsyncHTTPTestCase
from tornado import web


class Student(Resource):
    pass


class Teacher(Resource):
    pass


class TestJSAPI(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        Student.collection = OrderedDict()
        Student.id = 0

    def get_app(self):
        registry = Registry()
        registry.register(Student)
        registry.register(Teacher)
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
