import unittest

from tornadowebapi.exceptions import NotFound
from tornadowebapi.serializers import BasicRESTSerializer
from tornadowebapi.tests.resource_handlers import Student


class TestBasicRESTSerializer(unittest.TestCase):
    def test_serialize_items_response(self):
        students = [
            Student(id="1"),
            Student(id="2"),
            Student(id="3")
        ]

        serializer = BasicRESTSerializer()
        self.assertEqual(
            serializer.serialize_items_response(students),
            {"items": ["1", "2", "3"]})

    def test_serialize_resource(self):
        student = Student(id="1", name="john wick", age=39)

        serializer = BasicRESTSerializer()
        self.assertEqual(
            serializer.serialize_resource(student),
            {"age": 39,
             "name": "john wick",
             "id": "1"})
