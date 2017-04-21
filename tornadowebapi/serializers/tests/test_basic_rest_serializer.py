import unittest

from tornadowebapi.items_response import ItemsResponse
from tornadowebapi.serializers import BasicRESTSerializer
from tornadowebapi.tests.resource_handlers import Student, Teacher, City, \
    Person


class TestBasicRESTSerializer(unittest.TestCase):
    def test_serialize_items_response(self):
        students = ItemsResponse(
            type=Student,
            items=[
                Student(identifier="1"),
                Student(identifier="2"),
                Student(identifier="3")
            ],
            offset=0,
            total=30
        )

        serializer = BasicRESTSerializer()
        self.assertEqual(
            serializer.serialize_items_response(students),
            {
                "total": 30,
                "offset": 0,
                "items": {
                    "1": {},
                    "2": {},
                    "3": {}
                }
            })

    def test_serialize_resource(self):
        student = Student(identifier="1", name="john wick", age=39)

        serializer = BasicRESTSerializer()
        self.assertEqual(
            serializer.serialize_resource(student),
            {"age": 39,
             "name": "john wick"})

    def test_serialize_resource_with_default(self):
        teacher = Teacher(identifier="1",
                          name="john wick")

        serializer = BasicRESTSerializer()
        self.assertEqual(
            serializer.serialize_resource(teacher),
            {"name": "john wick"})

        teacher.age = 39
        self.assertEqual(
            serializer.serialize_resource(teacher),
            {"name": "john wick",
             "age": 39})

    def test_serialize_with_fragment(self):
        resource = City(
            identifier="1",
            name="Cambridge",
            mayor=Person(
                name="Jeremy Benstead",
                age=50,
            )
        )

        serializer = BasicRESTSerializer()
        result = serializer.serialize_resource(resource)
        self.assertEqual(result,
                         {
                             "name": "Cambridge",
                             "mayor": {
                                 "name": "Jeremy Benstead",
                                 "age": 50
                             }
                         })

    def test_serialize_non_webapi_exception(self):
        serializer = BasicRESTSerializer()

        with self.assertRaises(TypeError):
            serializer.serialize_exception(KeyError())
