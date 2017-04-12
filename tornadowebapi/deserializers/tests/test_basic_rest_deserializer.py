import unittest

from tornadowebapi.deserializers import BasicRESTDeserializer
from tornadowebapi.tests.resource_handlers import Student, Teacher
from tornadowebapi.traitlets import Absent


class TestBasicRESTDeserializer(unittest.TestCase):
    def test_basic_functionality(self):
        deserializer = BasicRESTDeserializer()
        res = deserializer.deserialize_resource(
            Student,
            "1",
            {"age": 39,
             "name": "john wick",
             "id": "1"})

        self.assertIsInstance(res, Student)
        self.assertEqual(res.age, 39)
        self.assertEqual(res.identifier, "1")
        self.assertEqual(res.name, "john wick")

    def test_optional_entries(self):
        deserializer = BasicRESTDeserializer()
        res = deserializer.deserialize_resource(
            Teacher,
            "1",
            {"age": 39,
             "name": "john wick",
             "discipline": ["chem", "phys"],
             "id": "1"})

        self.assertIsInstance(res, Teacher)
        self.assertEqual(res.age, 39)
        self.assertEqual(res.identifier, "1")
        self.assertEqual(res.name, "john wick")
        self.assertEqual(res.discipline, ["chem", "phys"])

        res = deserializer.deserialize_resource(
            Teacher,
            "1",
            {"name": "john wick",
             "discipline": ["chem", "phys"],
             "id": "1"})

        self.assertIsInstance(res, Teacher)
        self.assertEqual(res.age, Absent)
        self.assertEqual(res.identifier, "1")
        self.assertEqual(res.name, "john wick")
        self.assertEqual(res.discipline, ["chem", "phys"])
