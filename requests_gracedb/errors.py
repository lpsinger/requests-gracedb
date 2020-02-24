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


def _hook_raise_errors(response, *args, **kwargs):
    """Response hook to raise exception for any HTTP error (status >= 400)."""
    response.raise_for_status()


class SessionErrorMixin(object):
    """A mixin for :class:`requests.Session` to raise exceptions for HTTP
    errors.
    """

    def __init__(self, **kwargs):
        super(SessionErrorMixin, self).__init__(**kwargs)
        self.hooks['response'].append(_hook_raise_errors)
