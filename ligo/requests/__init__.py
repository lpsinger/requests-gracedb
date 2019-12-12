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
    pass