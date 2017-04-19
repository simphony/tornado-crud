import unittest

from tornadowebapi.items_response import ItemsResponse


class TestItemsResponse(unittest.TestCase):
    def test_set_from_list(self):
        response = ItemsResponse(int)

        response.set([1, 2, 3, 4])
        self.assertEqual(response.items, [1, 2, 3, 4])
        self.assertEqual(response.offset, 0)
        self.assertEqual(response.total, 4)

        with self.assertRaises(TypeError):
            response.set(["A", "B"])

        response.set([1, 2, 3, 4], 3, 8)
        self.assertEqual(response.offset, 3)
        self.assertEqual(response.total, 8)
