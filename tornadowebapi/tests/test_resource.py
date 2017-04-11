import unittest

from tornadowebapi.resource import Resource
from tornadowebapi.traitlets import Int, Unicode


class Student(Resource):
    name = Unicode()
    age = Int()


class TestResource(unittest.TestCase):
    def test_instantiation(self):
        s = Student("1")
        self.assertEqual(s.collection_name(), "students")
