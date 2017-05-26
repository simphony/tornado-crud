import unittest

from tornadowebapi.errors import Source, Error
from tornadowebapi.exceptions import ObjectNotFound, ValidationError


class TestExceptions(unittest.TestCase):
    def test_to_dict(self):
        exc = ObjectNotFound()
        self.assertEqual(
            exc.to_jsonapi(),
            [{
                "status": '404',
                "title": "Object not found"
            }])

    def test_multiple_errors(self):
        exc = ValidationError(
            errors=[
                Error(title="error 1",
                      source=Source(parameter="filter")
                      ),
                Error(title="error 2",
                      source=Source(parameter="sort")
                      ),
            ]
        )
        self.assertEqual(
            exc.to_jsonapi(),
            [
                {
                    "title": "error 1",
                    "source": {
                        "parameter": "filter"
                    }
                },
                {
                    "title": "error 2",
                    "source": {
                        "parameter": "sort"
                    }
                }
            ])
