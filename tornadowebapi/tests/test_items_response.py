import unittest

from tornadowebapi.items_response import ItemsResponse
from tornadowebapi.tests.resource_handlers import Student
from traitlets import TraitError


class TestItemsResponse(unittest.TestCase):
    def test_set_from_list(self):
        response = ItemsResponse(Student)

        items = [Student("1"),
                 Student("2"),
                 Student("3"),
                 Student("4")]
        response.set(items)
        self.assertEqual(response.items, items)
        self.assertEqual(response.offset, 0)
        self.assertEqual(response.total, 4)

        with self.assertRaises(TypeError):
            response.set(["A", "B"])

        response.set(items, 3, 8)
        self.assertEqual(response.offset, 3)
        self.assertEqual(response.total, 8)

    def test_no_type(self):
        response = ItemsResponse(None)

        response.set([1, 2, 3, 4])
        response.set(["A", "B"])

        self.assertEqual(response.items, ["A", "B"])

    def test_not_a_list(self):
        response = ItemsResponse(None)

        with self.assertRaises(TraitError):
            response.set("hello")
