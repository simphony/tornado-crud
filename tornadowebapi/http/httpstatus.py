"""
Deprecated module. Scheduled for removal in 0.3.0
Clients should use http.HTTPStatus directly instead.
"""
from http import HTTPStatus

for k, v in HTTPStatus.__members__.items():
    globals()[k] = v
