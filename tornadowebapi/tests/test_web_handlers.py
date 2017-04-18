import unittest
from unittest.mock import Mock, MagicMock

from tornadowebapi.web_handlers import CollectionWebHandler


class TestWebHandlers(unittest.TestCase):
    def test_query_arguments_as_dict(self):
        request = Mock()
        request.query_arguments = {
            "limit": ["5"],
            "offset": ["3"],
            "whatever": [],
            "items": ["1", "2"]

        }
        handler = CollectionWebHandler(MagicMock(), request,
                                       registry=MagicMock(),
                                       base_urlpath="/",
                                       api_version="1")
        self.assertEqual(
            handler.parsed_query_arguments(),
            {"limit": 5,
             "offset": 3,
             "items": ["1", "2"]
             }
        )
