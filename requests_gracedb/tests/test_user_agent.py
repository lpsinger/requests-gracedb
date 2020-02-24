#
# Copyright (C) 2019-2020  Leo P. Singer <leo.singer@ligo.org>
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
