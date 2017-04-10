import unittest

from tornadowebapi.deserializers import BasicRESTDeserializer
from tornadowebapi.exceptions import BadRepresentation
from tornadowebapi.tests.resource_handlers import Student, Teacher


class TestBasicRESTDeserializer(unittest.TestCase):
    def test_basic_functionality(self):
        deserializer = BasicRESTDeserializer()
        res = deserializer.deserialize_resource(
            Student,
            {"age": 39,
             "name": "john wick",
             "id": "1"})

        self.assertIsInstance(res, Student)
        self.assertEqual(res.age, 39)
        self.assertEqual(res.id, "1")
        self.assertEqual(res.name, "john wick")

    def test_optional_entries(self):
        deserializer = BasicRESTDeserializer()
        res = deserializer.deserialize_resource(
            Teacher,
            {"age": 39,
             "name": "john wick",
             "discipline": ["chem", "phys"],
             "id": "1"})

        self.assertIsInstance(res, Teacher)
        self.assertEqual(res.age, 39)
        self.assertEqual(res.id, "1")
        self.assertEqual(res.name, "john wick")
        self.assertEqual(res.discipline, ["chem", "phys"])

        res = deserializer.deserialize_resource(
            Teacher,
            {"name": "john wick",
             "discipline": ["chem", "phys"],
             "id": "1"})

        self.assertIsInstance(res, Teacher)
        self.assertEqual(res.age, 0)
        self.assertEqual(res.id, "1")
        self.assertEqual(res.name, "john wick")
        self.assertEqual(res.discipline, ["chem", "phys"])

        with self.assertRaises(BadRepresentation):
            deserializer.deserialize_resource(
                Teacher,
                {"discipline": ["chem", "phys"],
                 "id": "1"})
