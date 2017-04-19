import unittest

from tornadowebapi.resource_fragment import ResourceFragment
from tornadowebapi.resource import Resource, mandatory_absents, is_valid
from tornadowebapi.traitlets import Int, Unicode, OneOf


class Student(Resource):
    name = Unicode()
    age = Int()
    hair_color = Unicode(optional=True)


class Classroom(ResourceFragment):
    floor = Int()
    name = Unicode(optional=True)


class Teacher(Resource):
    name = Unicode()
    classroom = OneOf(Classroom)


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

    def test_mandatory_absents_with_fragments(self):
        t = Teacher("1")
        self.assertEqual(mandatory_absents(t), {"name", "classroom"})

        t.classroom = Classroom()
        self.assertEqual(mandatory_absents(t), {"name", "classroom.floor"})

        t.name = "Mr. Stevens"
        t.classroom.floor = 3

        self.assertEqual(mandatory_absents(t), set())

    def test_fill(self):
        t = Teacher("1")
        t.fill({
            "name": "Mr. Stevens",
            "classroom": {
                "floor": 3,
                "name": "Chemistry lab"
                }
        })

        self.assertEqual(t.name, "Mr. Stevens")
        self.assertIsInstance(t.classroom, Classroom)
        self.assertEqual(t.classroom.floor, 3)
        self.assertEqual(t.classroom.name, "Chemistry lab")

    def test_fill_with_object(self):
        t1 = Teacher("1")
        t1.fill({
            "name": "Mr. Stevens",
            "classroom": {
                "floor": 3,
                "name": "Chemistry lab"
            }
        })

        t2 = Teacher("2")
        t2.fill(t1)

        self.assertEqual(t2.name, "Mr. Stevens")
        self.assertIsInstance(t2.classroom, Classroom)
        self.assertEqual(t2.classroom.floor, 3)
        self.assertEqual(t2.classroom.name, "Chemistry lab")
