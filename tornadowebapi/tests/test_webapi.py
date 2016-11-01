import unittest
import urllib.parse
from collections import OrderedDict
from unittest import mock

import tornadowebapi
from tornadowebapi import registry
from tornadowebapi.http import httpstatus
from tornadowebapi.registry import Registry
from tornadowebapi.handler import ResourceHandler, CollectionHandler
from tornadowebapi.tests.resources import (
    AlreadyPresent, ExceptionValidated, NullReturningValidated,
    CorrectValidated, Broken, UnsupportsCollection, Unprocessable,
    UnsupportAll, Student, Teacher)
from tornadowebapi.tests.utils import AsyncHTTPTestCase
from tornado import web, escape


class TestREST(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        Student.collection = OrderedDict()
        Student.id = 0

    def get_app(self):
        handlers = tornadowebapi.api_handlers('/')
        registry.registry.register(Student)
        registry.registry.register(UnsupportAll)
        registry.registry.register(Unprocessable)
        registry.registry.register(UnsupportsCollection)
        registry.registry.register(Broken)
        registry.registry.register(ExceptionValidated)
        registry.registry.register(NullReturningValidated)
        registry.registry.register(CorrectValidated)
        registry.registry.register(AlreadyPresent)
        app = web.Application(handlers=handlers)
        app.hub = mock.Mock()
        return app

    def test_items(self):
        res = self.fetch("/api/v1/students/")

        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {"items": []})

        Student.collection[1] = ""
        Student.collection[2] = ""
        Student.collection[3] = ""

        res = self.fetch("/api/v1/students/")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {"items": ["1", "2", "3"]})

    def test_create(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        self.assertEqual(res.code, httpstatus.CREATED)
        self.assertIn("api/v1/students/0/", res.headers["Location"])

        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )
        self.assertEqual(res.code, httpstatus.CREATED)
        self.assertIn("api/v1/students/1/", res.headers["Location"])

        res = self.fetch("/api/v1/students/")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {"items": ['0', '1']})

    def test_retrieve(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        location = urllib.parse.urlparse(res.headers["Location"]).path

        res = self.fetch(location)
        self.assertEqual(res.code, httpstatus.OK)

        self.assertEqual(escape.json_decode(res.body),
                         {"foo": "bar"}
                         )

        res = self.fetch("/api/v1/students/1/")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)
        self.assertNotIn("Content-Type", res.headers)

    def test_post_on_resource(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        location = urllib.parse.urlparse(res.headers["Location"]).path
        res = self.fetch(
            location,
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        self.assertEqual(res.code, httpstatus.CONFLICT)

    def test_update(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        location = urllib.parse.urlparse(res.headers["Location"]).path

        res = self.fetch(
            location,
            method="PUT",
            body=escape.json_encode({
                "foo": "baz"
            })
        )
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

        res = self.fetch(location)
        self.assertEqual(escape.json_decode(res.body),
                         {"foo": "baz"}
                         )

        res = self.fetch(
            "/api/v1/students/1/",
            method="PUT",
            body=escape.json_encode({
                "foo": "bar"
            })
        )
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_delete(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        # Unfortunately, self.fetch wants a path and never consider
        # the possibility of a fqdn in the url, but according to
        # REST standard and HTTP standard, location should be absolute.
        location = urllib.parse.urlparse(res.headers["Location"]).path

        res = self.fetch(location, method="DELETE")
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

        res = self.fetch(location)
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch("/api/v1/students/1/", method="DELETE")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_unexistent_resource_type(self):
        res = self.fetch(
            "/api/v1/teachers/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch(
            "/api/v1/teachers/",
            method="GET",
        )

        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_post_non_json(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body="hello"
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_unsupported_methods(self):
        res = self.fetch(
            "/api/v1/unsupportalls/",
            method="POST",
            body="{}"
        )
        self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

        res = self.fetch(
            "/api/v1/unsupportalls/1/",
            method="GET",
        )
        self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

        res = self.fetch(
            "/api/v1/unsupportalls/1/",
            method="DELETE",
        )
        self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

        res = self.fetch(
            "/api/v1/unsupportalls/1/",
            method="PUT",
            body="{}"
        )
        self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

    def test_unprocessable(self):
        res = self.fetch(
            "/api/v1/unprocessables/",
            method="POST",
            body="{}"
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(res.headers["Content-Type"], 'application/json')
        self.assertEqual(escape.json_decode(res.body), {
            "type": "BadRepresentation",
            "message": "unprocessable",
            "foo": "bar",
        })

        res = self.fetch(
            "/api/v1/unprocessables/",
            method="GET",
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(res.headers["Content-Type"], 'application/json')
        self.assertEqual(escape.json_decode(res.body), {
            "type": "BadRepresentation",
            "message": "unprocessable",
            "foo": "bar",
        })

        res = self.fetch(
            "/api/v1/unprocessables/0/",
            method="PUT",
            body="{}"
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(res.headers["Content-Type"], 'application/json')
        self.assertEqual(escape.json_decode(res.body), {
            "type": "BadRepresentation",
            "message": "unprocessable",
            "foo": "bar",
        })

        res = self.fetch(
            "/api/v1/unprocessables/0/",
            method="GET",
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(res.headers["Content-Type"], 'application/json')
        self.assertEqual(escape.json_decode(res.body), {
            "type": "BadRepresentation",
            "message": "unprocessable",
            "foo": "bar",
        })

        res = self.fetch(
            "/api/v1/unprocessables/0/",
            method="POST",
            body="{}"
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(res.headers["Content-Type"], 'application/json')
        self.assertEqual(escape.json_decode(res.body), {
            "type": "BadRepresentation",
            "message": "unprocessable",
            "foo": "bar",
        })

    def test_broken(self):
        collection_url = "/api/v1/brokens/"

        for method, body in [("POST", "{}"), ("PUT", "{}"),
                             ("GET", None), ("DELETE", None)]:
            res = self.fetch(
                collection_url+"0/", method=method, body=body)
            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

        for method, body in [("POST", "{}"), ("GET", None)]:
            res = self.fetch(collection_url, method=method, body=body)
            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

    def test_unsupports_collections(self):
        res = self.fetch(
            "/api/v1/unsupportscollections/",
            method="GET")
        self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

    def test_validated(self):
        url = "/api/v1/exceptionvalidateds/"

        res = self.fetch(url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

        res = self.fetch(url+"0/", method="PUT", body="{}")
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

        url = "/api/v1/nullreturningvalidateds/"

        res = self.fetch(url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

        res = self.fetch(url+"0/", method="PUT", body="{}")
        self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

        url = "/api/v1/correctvalidateds/"

        res = self.fetch(url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.CREATED)

        res = self.fetch(url+"0/", method="PUT", body="{}")
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

    def test_exists(self):
        collection_url = "/api/v1/alreadypresents/"

        res = self.fetch(collection_url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.CONFLICT)


class TestRESTFunctions(unittest.TestCase):
    def test_api_handlers(self):
        handlers = tornadowebapi.api_handlers("/foo")
        self.assertEqual(handlers[0][0], "/foo/api/v1/(.*)/(.*)/")
        self.assertEqual(handlers[0][1], ResourceHandler)
        self.assertEqual(handlers[1][0], "/foo/api/v1/(.*)/")
        self.assertEqual(handlers[1][1], CollectionHandler)


class TestNonGlobalRegistry(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        Student.collection = OrderedDict()
        Student.id = 0

    def get_app(self):
        self.registry = Registry()
        self.registry.register(Teacher)
        handlers = self.registry.api_handlers('/')
        app = web.Application(handlers=handlers)
        return app

    def test_non_global_registry(self):
        res = self.fetch("/api/v1/teachers/")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {"items": []})
