import unittest

from tornadowebapi.exceptions import ObjectNotFound


class TestExceptions(unittest.TestCase):
    def test_to_dict(self):
        exc = ObjectNotFound({"foo": "bar"}, "baz")
        self.assertEqual(
            exc.to_dict(),
            {
                "source": {
                    "foo": "bar"
                },
                "detail": "baz",
                "status": 404,
                "title": "Object not found"
            })
