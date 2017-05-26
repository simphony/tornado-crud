import unittest

from tornadowebapi.exceptions import ObjectNotFound


class TestExceptions(unittest.TestCase):
    def test_to_dict(self):
        exc = ObjectNotFound()
        self.assertEqual(
            exc.to_jsonapi(),
            [{
                "status": '404',
                "title": "Object not found"
            }])
