from requests.sessions import Session

from .api import API
from .auth import SessionAuthMixin
from .file import SessionFileMixin

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ('Client',)


def _hook_raise_errors(response, *args, **kwargs):
    """Response hook to raise exception for any HTTP error (status >= 400)."""
    response.raise_for_status()


class Client(API, SessionFileMixin, SessionAuthMixin, Session):
    """GraceDB Client.

    Parameters
    ----------
    url : str
        GraceDB Client URL.
    cert : str, tuple
        Client-side X.509 certificate. May be either a single filename
        if the certificate and private key are concatenated together, or
        a tuple of the filenames for the certificate and private key.
    username : str
        Username for basic auth.
    password : str
        Password for basic auth.
    force_noauth : bool, default=False
        If true, then do not use any authentication at all.
    fail_noauth : bool, default=False
        If true, then raise an exception if authentication credentials are
        not provided.
    cert_reload : bool, default=False
        If true, then automatically reload the client certificate before it
        expires.
    cert_cert_reload_timeout : int, default=300
        Reload the certificate this many seconds before it expires.
    """

    def __init__(self, url='https://gracedb.ligo.org/api/', *args, **kwargs):
        super().__init__(url, *args, **kwargs)
        self.url = url
        self.headers['User-Agent'] = '{}/{}'.format(__name__, __version__)
        self.hooks['response'].append(_hook_raise_errors)
