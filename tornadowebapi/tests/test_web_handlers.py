import unittest
from unittest.mock import Mock, MagicMock

from tornadowebapi.web_handlers import WithoutIdentifierWebHandler


class TestWebHandlers(unittest.TestCase):
    def test_query_arguments_as_dict(self):
        request = Mock()
        request.query_arguments = {
            "limit": ["5"],
            "offset": ["3"],
            "whatever": [],
            "items": ["1", "2"]

        }
        handler = WithoutIdentifierWebHandler(MagicMock(), request,
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

    def test_check_resource_sanity(self):
        handler = WithoutIdentifierWebHandler(MagicMock(), MagicMock(),
                                              registry=MagicMock(),
                                              base_urlpath="/",
                                              api_version="1")

        with self.assertRaises(ValueError):
            handler._check_resource_sanity(Mock(), "whatever")

    def test_send_created_to_client(self):
        handler = WithoutIdentifierWebHandler(MagicMock(), MagicMock(),
                                              registry=MagicMock(),
                                              base_urlpath="/",
                                              api_version="1")

        with self.assertRaises(TypeError):
            handler._send_created_to_client("whatever")
