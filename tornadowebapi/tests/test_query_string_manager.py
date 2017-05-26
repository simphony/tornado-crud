import unittest

from marshmallow_jsonapi import Schema
from ..querystring import QueryStringManager as QSManager


class TestQueryStringManager(unittest.TestCase):
    def test_query_args(self):
        qs = QSManager({'page[number]': [b'1'],
                        'page[size]': [b'10'],
                        'foo': [b'bar', b'baz']
                        },
                       Schema)

        self.assertEqual(qs.query_args,
                         {'page[number]': '1',
                          'page[size]': '10',
                          'foo': ['bar', 'baz']}
                         )

    def test_pagination(self):
        qs = QSManager({'page[number]': [b'1'],
                        'page[size]': [b'10']},
                       Schema)
        self.assertEqual(
            qs.pagination['number'], 1
        )
        self.assertEqual(
            qs.pagination['size'], 10
        )

    def test_queryitems(self):
        qs = QSManager({'page[number]': [b'1'],
                        'page[size]': [b'10'],
                        'foo': [b'bar', b'baz']
                        },
                       Schema)

        items = qs.queryitems()
        self.assertIn(("page[number]", '1'), items)
        self.assertIn(("page[size]", '10'), items)
        self.assertIn(("foo", 'bar'), items)
        self.assertIn(("foo", 'baz'), items)

