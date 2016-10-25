from collections import OrderedDict
from unittest import mock

import tornadowebapi
from tornadowebapi import registry, exceptions
from tornadowebapi.http import httpstatus
from tornadowebapi.resource import Resource
from tornadowebapi.tests.utils import AsyncHTTPTestCase
from tornado import web, gen


def prepare_side_effect(*args, **kwargs):
    user = mock.Mock()
    user.orm_user = mock.Mock()
    args[0].current_user = user


class Student(Resource):

    collection = OrderedDict()
    id = 0

    @gen.coroutine
    def create(self, representation):
        id = type(self).id
        self.collection[str(id)] = representation
        type(self).id += 1
        return id

    @gen.coroutine
    def retrieve(self, identifier):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        return self.collection[identifier]

    @gen.coroutine
    def update(self, identifier, representation):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        self.collection[identifier] = representation

    @gen.coroutine
    def delete(self, identifier):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        del self.collection[identifier]

    @gen.coroutine
    def items(self):
        return list(self.collection.keys())


class TestJSAPI(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        Student.collection = OrderedDict()
        Student.id = 0

    def get_app(self):
        handlers = tornadowebapi.api_handlers('/')
        registry.registry.register(Student)
        app = web.Application(handlers=handlers)
        app.hub = mock.Mock()
        return app

    def test_items(self):
        res = self.fetch("/jsapi/v1/resources.js")
        print(res.body)
        self.assertEqual(res.code, httpstatus.OK)
