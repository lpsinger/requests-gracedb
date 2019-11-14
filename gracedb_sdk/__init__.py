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
    """GraceDB client session.

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

    Notes
    -----

    When a new Client instance is created, the following sources of
    authentication are tried, in order:

    1.  If the :obj:`force_noauth` keyword argument is true, then perform no
        authentication at all.

    2.  If the :obj:`cert` keyword argument is provided, then use X.509 client
        certificate authentication.

    3.  If the :obj:`username` and :obj:`password` keyword arguments are
        provided, then use basic auth.

    4.  Look for a default X.509 client certificate in:

        a.  the environment variables :envvar:`X509_USER_CERT` and
            :envvar:`X509_USER_KEY`
        b.  the environment variable :envvar:`X509_USER_PROXY`
        c.  the file :file:`/tmp/x509up_u{UID}`, where :samp:`{UID}` is your
            numeric user ID
        d.  the files :file:`~/.globus/usercert.pem` and
            :file:`~/.globus/userkey.pem`

    5.  Read the netrc file [1]_ located at :file:`~/.netrc`, or at the path stored
        in the environment variable :envvar:`NETRC`, and look for a username
        and password matching the hostname in the URL.

    6.  If the :obj:`fail_noauth` keyword argument is true, and no
        authentication source was found, then raise a :class:`ValueError`.

    References
    ----------
    .. [1] The .netrc file.
           https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html
    """  # noqa: E501

    def __init__(self, url='https://gracedb.ligo.org/api/', *args, **kwargs):
        super().__init__(url, *args, **kwargs)
        self.url = url
        self.headers['User-Agent'] = '{}/{}'.format(__name__, __version__)
        self.hooks['response'].append(_hook_raise_errors)
