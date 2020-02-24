#
# Copyright (C) 2011-2020  Leo P. Singer <leo.singer@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
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
