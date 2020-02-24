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
from ._version import get_versions


class SessionUserAgentMixin(object):
    """A mixin for :class:`requests.Session` to add a User-Agent header."""

    def __init__(self, **kwargs):
        super(SessionUserAgentMixin, self).__init__(**kwargs)
        version = get_versions()['version']
        self.headers['User-Agent'] = '{}/{}'.format(__package__, version)
