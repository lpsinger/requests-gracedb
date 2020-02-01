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
      (see :class:`~ligo.requests.auth.SessionAuthMixin`)

    * Raise exceptions based on HTTP status codes
      (see :class:`~ligo.requests.error.SessionErrorMixin`)

    * Automatically load POSTed files from disk, automatically guess MIME types
      (see :class:`~ligo.requests.file.SessionFileMixin`)

    * Add User-Agent string based on Python package name and version
      (see :class:`~ligo.requests.user_agent.SessionUserAgentMixin`)
    """
