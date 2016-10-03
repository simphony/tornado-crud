"""
Deprecated module. Scheduled for removal in 0.3.0
Clients should use http.HTTPStatus directly instead.
"""

# Note that this is deprecated in Python 3.5 itself, but kept for
# backward compatibility. Py3.5 and above should use http.HTTPStatus
from http.client import *  # noqa
