import unittest

from tornadowebapi.deserializers import BasicRESTDeserializer
from tornadowebapi.tests.resource_handlers import Student, Teacher, Person, \
    City
from tornadowebapi.traitlets import Absent


class TestBasicRESTDeserializer(unittest.TestCase):
    def test_basic_functionality(self):
        deserializer = BasicRESTDeserializer()
        res = deserializer.deserialize(
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
        res = deserializer.deserialize(
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

        res = deserializer.deserialize(
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

    def test_deserialize_with_fragment(self):
        data = {
            "name": "Cambridge",
            "mayor": {
                "name": "Jeremy Benstead",
                "age": 50
            }
        }

        deserializer = BasicRESTDeserializer()
        result = deserializer.deserialize(City, "1", data)

        self.assertIsInstance(result, City)
        self.assertEqual(result.identifier, "1")
        self.assertEqual(result.name, "Cambridge")
        self.assertIsInstance(result.mayor, Person)
        self.assertEqual(result.mayor.name, "Jeremy Benstead")
        self.assertEqual(result.mayor.age, 50)

    def test_invalid_resource(self):
        deserializer = BasicRESTDeserializer()
        with self.assertRaises(TypeError):
            deserializer.deserialize(str, None, None)
