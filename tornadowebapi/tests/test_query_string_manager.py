import unittest

from marshmallow_jsonapi import Schema
from tornadowebapi.querystring import QueryStringManager as QSManager


class TestQueryStringManager(unittest.TestCase):
    def test_initialization(self):
        qs = QSManager({'page[number]': [b'1']}, Schema)
        qs.pagination

