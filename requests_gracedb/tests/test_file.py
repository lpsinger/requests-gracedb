"""Tests for :mod:`requests_gracedb.file`."""
from __future__ import absolute_import
from mimetypes import guess_type
try:
    from unittest.mock import Mock
except ImportError:  # FIXME: Python 2
    from mock import Mock

import requests
import pytest

from .. import Session


@pytest.fixture
def mock_request(monkeypatch):
    """Mock up requests.Session base class methods."""
    mock = Mock()
    monkeypatch.setattr(requests.Session, 'request', mock)
    return mock


def test_filename_and_contents(mock_request, tmpdir):
    """Test handling of various styles of POSTed files."""
    # Different operating systems return different MIME types for *.xml files:
    # application/xml on macOS, text/xml on Linux.
    xml_mime_type, _ = guess_type('example.xml')

    client = Session('https://example.org/')
    filename = str(tmpdir / 'coinc.xml')
    filecontent = b'<!--example data-->'
    with open(filename, 'wb') as f:
        f.write(filecontent)
    file_expected = ('coinc.xml', filecontent, xml_mime_type)

    file_in = ('coinc.xml', filecontent)
    client.post('https://example.org/', files={'key': file_in})
    assert mock_request.call_args[1]['files'] == [('key', file_expected)]

    file_in = (filename, None)
    client.post('https://example.org/', files={'key': file_in})
    assert mock_request.call_args[1]['files'] == [('key', file_expected)]

    with open(filename, 'rb') as fileobj:
        file_in = fileobj
        file_expected = ('coinc.xml', fileobj, xml_mime_type)
        client.post('https://example.org/', files={'key': file_in})
        assert mock_request.call_args[1]['files'] == [('key', file_expected)]
