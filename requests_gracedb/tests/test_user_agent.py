"""Tests for :mod:`requests_gracedb.user_agent`."""
import pytest

from .. import __version__
from .. import Session

# FIXME: Python 2
pytest.importorskip('pytest_httpserver')


def test_user_agent(socket_enabled, httpserver):
    """Test that the User-Agent HTTP header is populated."""
    expected_user_agent = 'requests_gracedb/{}'.format(__version__)

    httpserver.expect_oneshot_request(
        '/', headers={'User-Agent': expected_user_agent}
    ).respond_with_data(
        'OK'
    )

    url = httpserver.url_for('/')
    client = Session(url)
    with httpserver.wait():
        client.get(url)
