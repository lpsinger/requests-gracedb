"""Tests for :mod:`gracedb_sdk.file`."""
from unittest.mock import Mock

import pkg_resources
import requests
import pytest

from .. import Client


@pytest.fixture
def mock_request(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(requests.Session, 'request', mock)
    return mock


def test_filename_and_contents(mock_request):
    client = Client()
    filename = pkg_resources.resource_filename(__name__, 'data/coinc.xml')
    filecontent = pkg_resources.resource_string(__name__, 'data/coinc.xml')
    file_expected = ('coinc.xml', filecontent, 'application/xml')

    file_in = ('coinc.xml', filecontent)
    client.post('https://example.org/', files={'key': file_in})
    assert mock_request.call_args[1]['files'] == [('key', file_expected)]

    file_in = (filename, None)
    client.post('https://example.org/', files={'key': file_in})
    assert mock_request.call_args[1]['files'] == [('key', file_expected)]

    with open(filename, 'rb') as fileobj:
        file_in = fileobj
        file_expected = ('coinc.xml', fileobj, 'application/xml')
        client.post('https://example.org/', files={'key': file_in})
        assert mock_request.call_args[1]['files'] == [('key', file_expected)]
