import os
from os import getuid
from six.moves.urllib.parse import urlparse

from safe_netrc import netrc

from .cert_reload import CertReloadingHTTPAdapter


def _find_x509_credentials():
    """Try to find a user's X509 certificate and key.

    Checks environment variables first, then expected location for default
    proxy.
    """
    cert_file = os.environ.get('X509_USER_CERT')
    key_file = os.environ.get('X509_USER_KEY')
    if cert_file and key_file:
        return cert_file, key_file

    proxy_file = os.environ.get('X509_USER_PROXY')
    if proxy_file:
        return proxy_file

    # Try default proxy
    proxy_file = os.path.join('/tmp', 'x509up_u{}'.format(getuid()))
    if os.path.exists(proxy_file):
        return proxy_file

    # Try default cert/key
    home_dir = os.environ.get('HOME')
    if home_dir:
        cert_file = os.path.join(home_dir, '.globus', 'usercert.pem')
        key_file = os.path.join(home_dir, '.globus', 'userkey.pem')
        if os.path.exists(cert_file) and os.path.exists(key_file):
            return cert_file, key_file

    return None


def _find_username_password(url):
    host = urlparse(url).hostname

    try:
        result = netrc().authenticators(host)
    except IOError:
        result = None

    if result is not None:
        username, _, password = result
        result = (username, password)

    return result


class SessionAuthMixin(object):
    """A mixin for :class:`requests.Session` to add support for all GraceDB
    authentication mechanisms.

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
    fail_if_noauth : bool, default=False
        If true, then raise an exception if authentication credentials are
        not provided.
    cert_reload : bool, default=False
        If true, then automatically reload the client certificate before it
        expires.
    cert_reload_timeout : int, default=300
        Reload the certificate this many seconds before it expires.

    Notes
    -----
    When a new Session instance is created, the following sources of
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

    6.  If the :obj:`fail_if_noauth` keyword argument is true, and no
        authentication source was found, then raise a :class:`ValueError`.

    References
    ----------
    .. [1] The .netrc file.
           https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html

    """  # noqa: E501

    def __init__(self, url=None, cert=None, username=None, password=None,
                 force_noauth=False, fail_if_noauth=False, cert_reload=False,
                 cert_reload_timeout=300, **kwargs):
        super(SessionAuthMixin, self).__init__(**kwargs)

        # Support for reloading client certificates
        if cert_reload:
            self.mount('https://', CertReloadingHTTPAdapter(
                cert_reload_timeout=cert_reload_timeout))

        # Argument validation
        if fail_if_noauth and force_noauth:
            raise ValueError(
                'Must not set both force_noauth and fail_if_noauth.')
        if (username is None) ^ (password is None):
            raise ValueError('Must provide username and password, or neither.')

        # FIXME: these should go into elif clauses below
        # (as in `elif default_cert := _find_x509_credentials():`)
        # in order to defer unnecessary I/O,  but this requires
        # the := operator, which requires Python 3.8.
        default_cert = _find_x509_credentials()
        default_basic_auth = _find_username_password(url)

        if force_noauth:
            pass
        elif cert is not None:
            self.cert = cert
        elif username is not None:
            self.auth = (username, password)
        elif default_cert is not None:
            self.cert = default_cert
        elif default_basic_auth is not None:
            self.auth = default_basic_auth
        elif fail_if_noauth:
            raise ValueError('No authentication credentials found.')
