import unittest
import urllib.parse
from collections import OrderedDict
from unittest import mock

from tornado.testing import LogTrapTestCase
from tornadowebapi.http import httpstatus
from tornadowebapi.registry import Registry
from tornadowebapi.traitlets import Absent
from tornadowebapi.web_handlers import (
    WithIdentifierWebHandler, WithoutIdentifierWebHandler)
from tornadowebapi.tests import resource_handlers
from tornadowebapi.tests.utils import AsyncHTTPTestCase
from tornado import web, escape

ALL_RESOURCES = (
    resource_handlers.AlreadyPresentHandler,
    resource_handlers.ExceptionValidatedHandler,
    resource_handlers.NullReturningValidatedHandler,
    resource_handlers.CorrectValidatedHandler,
    resource_handlers.OurExceptionValidatedHandler,
    resource_handlers.BrokenHandler,
    resource_handlers.UnsupportsCollectionHandler,
    resource_handlers.UnprocessableHandler,
    resource_handlers.UnsupportAllHandler,
    resource_handlers.StudentHandler,
    resource_handlers.TeacherHandler,
    resource_handlers.InvalidIdentifierHandler,
    resource_handlers.OurExceptionInvalidIdentifierHandler,
    resource_handlers.ServerInfoHandler,
)


class TestWebAPI(AsyncHTTPTestCase, LogTrapTestCase):
    def setUp(self):
        super().setUp()
        resource_handlers.StudentHandler.collection = OrderedDict()
        resource_handlers.StudentHandler.id = 0
        resource_handlers.ServerInfoHandler.instance = {}
        resource_handlers.StudentHandler.id = 0

    def get_app(self):
        registry = Registry()
        handlers = registry.api_handlers('/')
        for resource in ALL_RESOURCES:
            registry.register(resource)
        app = web.Application(handlers=handlers)
        app.hub = mock.Mock()
        return app

    def test_items(self):
        res = self.fetch("/api/v1/students/")

        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "total": 0,
                             "offset": 0,
                             "items": {},
                             "identifiers": []
                         })

        handler = resource_handlers.StudentHandler
        handler.collection[1] = handler.resource_class(
            identifier="1",
            name="john wick",
            age=39)
        handler.collection[2] = handler.resource_class(
            identifier="2",
            name="john wick 2",
            age=39)
        handler.collection[3] = handler.resource_class(
            identifier="3",
            name="john wick 3",
            age=39)

        res = self.fetch("/api/v1/students/")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "total": 3,
                             "offset": 0,
                             "items": {
                                 "1": {
                                     "name": "john wick",
                                     "age": 39,
                                 },
                                 "2": {
                                     "name": "john wick 2",
                                     "age": 39,
                                 },
                                 "3": {
                                     "name": "john wick 3",
                                     "age": 39,
                                 }
                             },
                             "identifiers": ["1", "2", "3"]
                         })

    def test_items_with_query_params(self):
        res = self.fetch("/api/v1/students/?limit=1")

        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {"total": 0,
                          "offset": 0,
                          "items": {},
                          "identifiers": []
                          })

        res = self.fetch("/api/v1/students/?offset=1")

        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "total": 0,
                             "offset": 1,
                             "items": {},
                             "identifiers": []
                         })

        res = self.fetch("/api/v1/students/?offset=1&limit=1")

        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "total": 0,
                             "offset": 1,
                             "items": {},
                             "identifiers": []
                         })

        handler = resource_handlers.StudentHandler
        handler.collection[1] = handler.resource_class(
            identifier="1",
            name="john wick",
            age=39)
        handler.collection[2] = handler.resource_class(
            identifier="2",
            name="john wick 2",
            age=39)
        handler.collection[3] = handler.resource_class(
            identifier="3",
            name="john wick 3",
            age=39)

        res = self.fetch("/api/v1/students/?limit=2")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "total": 3,
                             "offset": 0,
                             "items": {
                                 "1": {
                                     "name": "john wick",
                                     "age": 39,
                                 },
                                 "2": {
                                     "name": "john wick 2",
                                     "age": 39,
                                 }
                             },
                             "identifiers": ["1", "2"],
                         })

        res = self.fetch("/api/v1/students/?offset=1")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "total": 3,
                             "offset": 1,
                             "items": {
                                 "2": {
                                     "name": "john wick 2",
                                     "age": 39,
                                 },
                                 "3": {
                                     "name": "john wick 3",
                                     "age": 39,
                                 }
                             },
                             "identifiers": ["2", "3"],
                         })

        res = self.fetch("/api/v1/students/?offset=1&limit=1")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "total": 3,
                             "offset": 1,
                             "items": {
                                 "2": {
                                     "name": "john wick 2",
                                     "age": 39,
                                 }
                             },
                             "identifiers": ["2"],
                         })

    def test_create(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
            })
        )

        self.assertEqual(res.code, httpstatus.CREATED)
        self.assertIn("api/v1/students/0/", res.headers["Location"])

        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick 2",
                "age": 19,
            })
        )
        self.assertEqual(res.code, httpstatus.CREATED)
        self.assertIn("api/v1/students/1/", res.headers["Location"])

        res = self.fetch("/api/v1/students/")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {"offset": 0,
                          "total": 2,
                          "items": {
                              "0": {"age": 19,
                                    "name": "john wick"
                                    },
                              "1": {"age": 19,
                                    "name": "john wick 2"
                                    },
                          },
                          "identifiers": ["0", "1"],
                          })

        # incorrect value for age
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
                "age": "hello",
            })
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

        # Missing mandatory entry
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
            })
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_retrieve(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
            })
        )

        location = urllib.parse.urlparse(res.headers["Location"]).path

        res = self.fetch(location)
        self.assertEqual(res.code, httpstatus.OK)

        self.assertEqual(escape.json_decode(res.body),
                         {"name": "john wick",
                          "age": 19}
                         )

        res = self.fetch("/api/v1/students/1/")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)
        self.assertNotIn("Content-Type", res.headers)

        handler = resource_handlers.StudentHandler
        handler.collection["0"].age = Absent

        # Verify output checks
        res = self.fetch(location)
        self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

    def test_post_on_resource(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
            })
        )

        location = urllib.parse.urlparse(res.headers["Location"]).path
        res = self.fetch(
            location,
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
            })
        )

        self.assertEqual(res.code, httpstatus.CONFLICT)

    def test_update(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
            })
        )

        location = urllib.parse.urlparse(res.headers["Location"]).path
        res = self.fetch(
            location,
            method="PUT",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
            })
        )
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

        res = self.fetch(location)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "name": "john wick",
                             "age": 19,
                         })

        # Incorrect type
        res = self.fetch(
            location,
            method="PUT",
            body=escape.json_encode({
                "name": "john wick",
                "age": "hello",
            })
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

        res = self.fetch(
            "/api/v1/students/1/",
            method="PUT",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
            })
        )
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        # Missing mandatory entry
        res = self.fetch(
            location,
            method="PUT",
            body=escape.json_encode({
                "name": "john wick",
            })
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_delete(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
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

    def test_delete_collection(self):
        res = self.fetch("/api/v1/students/", method="DELETE")
        self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

    def test_put_collection(self):
        res = self.fetch("/api/v1/students/",
                         method="PUT",
                         body=escape.json_encode({
                             "name": "john wick",
                             "age": 19,
                         }))
        self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

    def test_unexistent_resource_type(self):
        res = self.fetch(
            "/api/v1/notpresent/",
            method="POST",
            body=escape.json_encode({
                "name": "john wick",
                "age": 19,
            })
        )

        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch(
            "/api/v1/notpresent/",
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

        url = "/api/v1/nullreturningvalidateds/"

        res = self.fetch(url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

        url = "/api/v1/correctvalidateds/"

        res = self.fetch(url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.CREATED)

        url = "/api/v1/ourexceptionvalidateds/"

        res = self.fetch(url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_validate_identifier(self):
        url = "/api/v1/invalididentifiers/whoo/"

        res = self.fetch(url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch(url, method="PUT", body="{}")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch(url, method="GET")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch(url, method="DELETE")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        url = "/api/v1/ourexceptioninvalididentifiers/whoo/"

        res = self.fetch(url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

        res = self.fetch(url, method="PUT", body="{}")
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

        res = self.fetch(url, method="GET")
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

        res = self.fetch(url, method="DELETE")
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_exists(self):
        collection_url = "/api/v1/alreadypresents/"

        res = self.fetch(collection_url, method="POST", body="{}")
        self.assertEqual(res.code, httpstatus.CONFLICT)

    def test_items_with_arguments(self):
        collection_url = "/api/v1/students/?foo=bar&bar=baz&foo=meh"

        res = self.fetch(collection_url, method="GET")
        self.assertEqual(res.code, httpstatus.OK)

    def test_singleton_create(self):
        res = self.fetch("/api/v1/serverinfo/", method="GET")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch(
            "/api/v1/serverinfo/",
            method="POST",
            body=escape.json_encode({
                "status": "ok",
                "uptime": 1000,
            })
        )

        self.assertEqual(res.code, httpstatus.CREATED)
        self.assertIn("api/v1/serverinfo/", res.headers["Location"])

        res = self.fetch("/api/v1/serverinfo/", method="GET")
        self.assertEqual(res.code, httpstatus.OK)

        res = self.fetch(
            "/api/v1/serverinfo/",
            method="POST",
            body=escape.json_encode({
                "status": "ok",
                "uptime": 1000,
            })
        )
        self.assertEqual(res.code, httpstatus.CONFLICT)

    def test_singleton_delete(self):
        res = self.fetch("/api/v1/serverinfo/", method="DELETE")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch(
            "/api/v1/serverinfo/",
            method="POST",
            body=escape.json_encode({
                "status": "ok",
                "uptime": 1000,
            })
        )
        self.assertEqual(res.code, httpstatus.CREATED)

        res = self.fetch("/api/v1/serverinfo/", method="GET")
        self.assertEqual(res.code, httpstatus.OK)

        res = self.fetch("/api/v1/serverinfo/", method="DELETE")
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

        res = self.fetch("/api/v1/serverinfo/", method="GET")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_singleton_put(self):
        res = self.fetch(
            "/api/v1/serverinfo/",
            method="PUT",
            body=escape.json_encode({
                "status": "ok",
                "uptime": 1000,
            }))

        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch(
            "/api/v1/serverinfo/",
            method="POST",
            body=escape.json_encode({
                "status": "ok",
                "uptime": 1000,
            }))

        res = self.fetch(
            "/api/v1/serverinfo/",
            method="PUT",
            body=escape.json_encode({
                "status": "ok",
                "uptime": 2000,
            }))

        res = self.fetch("/api/v1/serverinfo/", method="GET")
        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {"status": "ok",
                          "uptime": 2000})


class TestRESTFunctions(unittest.TestCase):
    def test_api_handlers(self):
        reg = Registry()
        handlers = reg.api_handlers("/foo")
        self.assertEqual(handlers[0][0], "/foo/api/v1/(.*)/(.*)/")
        self.assertEqual(handlers[0][1], WithIdentifierWebHandler)
        self.assertEqual(handlers[1][0], "/foo/api/v1/(.*)/")
        self.assertEqual(handlers[1][1], WithoutIdentifierWebHandler)
