"""Tests for :mod:`requests_gracedb.errors`."""
from __future__ import absolute_import
from requests.exceptions import HTTPError
import pytest

from .. import Session

# FIXME: Python 2
pytest.importorskip('pytest_httpserver')


def test_errors(socket_enabled, httpserver):
    """Test that HTTP 400 responses result in exceptions."""
    message = 'Tea time!'
    status = 418
    httpserver.expect_request('/').respond_with_data(message, status)

    url = httpserver.url_for('/')
    client = Session(url)
    with pytest.raises(HTTPError) as excinfo:
        client.get(url)
    exception = excinfo.value
    assert exception.response.status_code == status
    assert exception.response.reason == "I'M A TEAPOT"
    assert exception.response.text == message
