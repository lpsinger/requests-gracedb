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
from __future__ import absolute_import

import requests.sessions

from .auth import SessionAuthMixin
from .errors import SessionErrorMixin
from .file import SessionFileMixin
from .user_agent import SessionUserAgentMixin

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ('Session',)


class Session(SessionAuthMixin,
              SessionErrorMixin,
              SessionFileMixin,
              SessionUserAgentMixin,
              requests.sessions.Session):
    """A :class:`requests.Session` subclass that adds behaviors that are common
    to ligo.org REST API services such as that of :doc:`GraceDB
    <gracedb:index>`.

    It adds the following behaviors to the session:

    * GraceDB-style authentication
      (see :class:`~requests_gracedb.auth.SessionAuthMixin`)

    * Raise exceptions based on HTTP status codes
      (see :class:`~requests_gracedb.errors.SessionErrorMixin`)

    * Automatically load POSTed files from disk, automatically guess MIME types
      (see :class:`~requests_gracedb.file.SessionFileMixin`)

    * Add User-Agent string based on Python package name and version
      (see :class:`~requests_gracedb.user_agent.SessionUserAgentMixin`)
    """
