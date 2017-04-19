import unittest

from tornadowebapi.items_response import ItemsResponse
from tornadowebapi.serializers import BasicRESTSerializer
from tornadowebapi.tests.resource_handlers import Student, Teacher


class TestBasicRESTSerializer(unittest.TestCase):
    def test_serialize_items_response(self):
        students = ItemsResponse(
            type=Student,
            items=[
                Student(identifier="1"),
                Student(identifier="2"),
                Student(identifier="3")
            ],
            index_first=0,
            num_items=3,
            total_items=30
        )

        serializer = BasicRESTSerializer()
        self.assertEqual(
            serializer.serialize_items_response(students),
            {"items": ["1", "2", "3"]})

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

    def test_serialize_non_webapi_exception(self):
        serializer = BasicRESTSerializer()

        with self.assertRaises(TypeError):
            serializer.serialize_exception(KeyError())
