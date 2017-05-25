import unittest
import urllib.parse
from collections import OrderedDict
from unittest import mock
import http.client


from tornado.testing import LogTrapTestCase
from tornadowebapi.registry import Registry
from tornadowebapi.resource import (
    ResourceList, ResourceDetails)
from tornadowebapi.tests import resource_handlers
from tornadowebapi.tests.utils import AsyncHTTPTestCase
from tornado import web, escape


class TestWebAPI(AsyncHTTPTestCase, LogTrapTestCase):
    def setUp(self):
        super().setUp()
        resource_handlers.StudentDetails.model_connector.collection = \
            OrderedDict()
        resource_handlers.StudentDetails.model_connector.id = 0
        #resource_handlers.ServerInfoDetails.model_connector.instance = {}
        #resource_handlers.StudentDetails.model_connector.id = 0

    def get_app(self):
        registry = Registry()
        '''
        registry.register(
            resource_handlers.AlreadyPresentList,
            "/alreadypresents/",
        )
        registry.register(
            resource_handlers.AlreadyPresentDetails,
            "/alreadypresents/(.*)/",
        )
        registry.register(
            resource_handlers.BrokenList,
            "/brokens/",
        )
        registry.register(
            resource_handlers.BrokenDetails,
            "/brokens/(.*)/",
        )
        registry.register(
            resource_handlers.UnsupportsCollectionList,
            "/unsupportscollections/",
        )
        registry.register(
            resource_handlers.UnprocessableList,
            "/unprocessables/",
        )
        registry.register(
            resource_handlers.UnprocessableDetails,
            "/unprocessables/(.*)/",
        )
        registry.register(
            resource_handlers.UnsupportAllDetails,
            "/unsupportalls/(.*)/",
        )
        registry.register(
            resource_handlers.UnsupportAllList,
            "/unsupportalls/",
        )
        '''
        registry.register(
            resource_handlers.StudentList,
            "/students/",
        )
        registry.register(
            resource_handlers.StudentDetails,
            "/students/(.*)/",
        )
        '''
        registry.register(
            resource_handlers.TeacherDetails,
            "/teachers/(.*)/"
        )
        registry.register(
            resource_handlers.ServerInfoDetails,
            "/serverinfo/"
        )
        '''
        handlers = registry.api_handlers('/')
        app = web.Application(handlers=handlers, debug=True)
        app.hub = mock.Mock()
        return app

    def test_items(self):
        res = self.fetch("/api/v1/students/")

        self.assertEqual(res.code, http.client.OK)
        # self.assertEqual(escape.json_decode(res.body),
        #                  {
        #                      "total": 0,
        #                      "offset": 0,
        #                      "items": {},
        #                      "identifiers": []
        #                  })

        resource = resource_handlers.StudentDetails
        connector = resource.model_connector

        connector.collection[1] = dict(
            id="1",
            name="john wick",
            age=39)
        connector.collection[2] = dict(
            id="2",
            name="john wick 2",
            age=39)
        connector.collection[3] = dict(
            id="3",
            name="john wick 3",
            age=39)

        res = self.fetch("/api/v1/students/")
        self.assertEqual(res.code, http.client.OK)

        # self.assertEqual(escape.json_decode(res.body),
        #                  {
        #                      "total": 3,
        #                      "offset": 0,
        #                      "items": {
        #                          "1": {
        #                              "name": "john wick",
        #                              "age": 39,
        #                          },
        #                          "2": {
        #                              "name": "john wick 2",
        #                              "age": 39,
        #                          },
        #                          "3": {
        #                              "name": "john wick 3",
        #                              "age": 39,
        #                          }
        #                      },
        #                      "identifiers": ["1", "2", "3"]
        #                  })
    '''
    def test_items_with_limit_params(self):
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

        resource = resource_handlers.StudentDetails
        connector = resource.model_connector
        connector.collection[1] = resource.schema(
            identifier="1",
            name="john wick",
            age=39)
        connector.collection[2] = resource.schema(
            identifier="2",
            name="john wick 2",
            age=39)
        connector.collection[3] = resource.schema(
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

    def test_items_with_broken_limit_offset(self):
        res = self.fetch("/api/v1/students/?limit=hello")

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

        res = self.fetch("/api/v1/students/?offset=hello")

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_items_with_filter(self):
        res = self.fetch(
            '/api/v1/students/?filter={%22name%22:%22john%20wick%22}')

        self.assertEqual(res.code, httpstatus.OK)
        self.assertEqual(escape.json_decode(res.body),
                         {"total": 0,
                          "offset": 0,
                          "items": {},
                          "identifiers": []
                          })

        resource = resource_handlers.StudentDetails
        connector = resource.model_connector
        connector.collection[1] = resource.schema(
            identifier="1",
            name="john wick",
            age=39)
        connector.collection[2] = resource.schema(
            identifier="2",
            name="john wick 2",
            age=39)
        connector.collection[3] = resource.schema(
            identifier="3",
            name="john wick 3",
            age=39)

        res = self.fetch(
            '/api/v1/students/?filter={%22name%22:%22john%20wick%22}')
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
                             },
                             "identifiers": ["1"],
                         })

    def test_items_with_filter_broken_request(self):
        res = self.fetch(
            '/api/v1/students/?filter={%22name%22:%22john')
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
    '''

    def test_create(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "data": {
                        "type": "student",
                        "attributes": {
                            "name": "john wick",
                            "age": 19,
                        }
                }
            })
        )

        self.assertEqual(res.code, http.client.CREATED)
        self.assertIn("api/v1/students/0/", res.headers["Location"])

        # res = self.fetch(
        #     "/api/v1/students/",
        #     method="POST",
        #     body=escape.json_encode({
        #         "name": "john wick 2",
        #         "age": 19,
        #     })
        # )
        # self.assertEqual(res.code, http.client.CREATED)
        # self.assertIn("api/v1/students/1/", res.headers["Location"])
        #
        # res = self.fetch("/api/v1/students/")
        # self.assertEqual(res.code, http.client.OK)
        # self.assertEqual(escape.json_decode(res.body),
        #                  {"offset": 0,
        #                   "total": 2,
        #                   "items": {
        #                       "0": {"age": 19,
        #                             "name": "john wick"
        #                             },
        #                       "1": {"age": 19,
        #                             "name": "john wick 2"
        #                             },
        #                   },
        #                   "identifiers": ["0", "1"],
        #                   })
        #
        # # incorrect value for age
        # res = self.fetch(
        #     "/api/v1/students/",
        #     method="POST",
        #     body=escape.json_encode({
        #         "name": "john wick",
        #         "age": "hello",
        #     })
        # )
        # self.assertEqual(res.code, http.client.BAD_REQUEST)
        #
        # # Missing mandatory entry
        # res = self.fetch(
        #     "/api/v1/students/",
        #     method="POST",
        #     body=escape.json_encode({
        #         "name": "john wick",
        #     })
        # )
        # self.assertEqual(res.code, http.client.BAD_REQUEST)
'''
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

        handler = resource_handlers.StudentModelConn
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

    def test_singleton_create_with_invalid_type(self):
        res = self.fetch(
            "/api/v1/serverinfo/",
            method="POST",
            body=escape.json_encode({
                "status": "ok",
                "uptime": "hello",
            })
        )
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

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

    def test_put_invalid_type(self):
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
                "uptime": "hello",
            }))

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)


class TestRESTFunctions(unittest.TestCase):
    def test_api_handlers(self):
        reg = Registry()
        reg.register(resource_handlers.StudentList, "/students/")
        reg.register(resource_handlers.StudentDetails, "/students/(.*)/")
        handlers = reg.api_handlers("/foo")
        self.assertEqual(handlers[0][0], "/foo/api/v1/students/")
        self.assertTrue(issubclass(handlers[0][1], ResourceList))
        self.assertEqual(handlers[1][0], "/foo/api/v1/students/(.*)/")
        self.assertTrue(issubclass(handlers[1][1], ResourceDetails))
'''
