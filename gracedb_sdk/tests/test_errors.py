from requests.exceptions import HTTPError
import pytest

from .. import Client


def test_errors(socket_enabled, httpserver):
    message = 'Tea time!'
    status = 418
    httpserver.expect_request('/').respond_with_data(message, status)

    url = httpserver.url_for('/')
    client = Client(url)
    with pytest.raises(HTTPError) as excinfo:
        client.get(url)
    exception = excinfo.value
    assert exception.response.status_code == status
    assert exception.response.reason == "I'M A TEAPOT"
    assert exception.response.text == message
