import unittest

from tornadowebapi.resource import Resource, mandatory_absents, is_valid
from tornadowebapi.traitlets import Int, Unicode


class Student(Resource):
    name = Unicode()
    age = Int()
    hair_color = Unicode(optional=True)


class TestResource(unittest.TestCase):
    def test_instantiation(self):
        s = Student("1")
        self.assertEqual(s.collection_name(), "students")

    def test_mandatory_absents(self):
        s = Student("1")
        self.assertEqual(
            mandatory_absents(s),
            {"name", "age"})
        self.assertFalse(is_valid(s))

        s.age = 15

        self.assertEqual(
            mandatory_absents(s),
            {"name"})
        self.assertFalse(is_valid(s))

        s.name = "hello"

        self.assertEqual(
            mandatory_absents(s),
            set())
        self.assertTrue(is_valid(s))

        s.identifier = None
        self.assertFalse(is_valid(s))
