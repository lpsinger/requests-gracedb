import os
from os import getuid
from urllib.parse import urlparse
from warnings import warn

from requests import status_codes
from safe_netrc import netrc

from .cert_reload import CertReloadingHTTPAdapter


def find_x509_credentials():
    """Try to find a user's X509 certificate and key.

    Checks environment variables first, then expected location for default
    proxy.
    """
    proxy_file = os.environ.get('X509_USER_PROXY')
    cert_file = os.environ.get('X509_USER_CERT')
    key_file = os.environ.get('X509_USER_KEY')

    if cert_file and key_file:
        return cert_file, key_file

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


def find_username_password(url):
    host = urlparse(url).hostname
    username = password = None

    try:
        result = netrc().authenticators(host)
    except IOError:
        result = None

    if result:
        username, _, password = result

    return username, password


def _hook_warn_basic_auth(response, *args, **kwargs):
    """Response hook to print a warning for basic auth problems."""
    if response.status_code == status_codes.unauthorized:
        warn('Please check the username/password in your .netrc file. If your '
             'password is more than a year old, you will need to use the web '
             'interface to generate a new one.')


class SessionAuthMixin:
    """A mixin for :class:`requests.Session` to add support for all GraceDB
    authentication mechanisms."""

    def __init__(self, url=None, cert=None, username=None, password=None,
                 force_noauth=False, fail_noauth=False, cert_reload=False,
                 cert_reload_timeout=300):
        super().__init__()

        # Support for reloading client certificates
        if cert_reload:
            self.mount('https://', CertReloadingHTTPAdapter(
                cert_reload_timeout=cert_reload_timeout))

        # Argument validation
        if fail_noauth and force_noauth:
            raise ValueError('Must not set both force_noauth and fail_noauth.')
        if (username is None) ^ (password is None):
            raise ValueError('Must provide username and password, or neither.')

        default_cert = find_x509_credentials()
        default_username, default_password = find_username_password(url)

        if force_noauth:
            pass
        elif cert is not None:
            self.cert = cert
        elif username is not None:
            self.auth = (username, password)
            self.hooks['response'].append(_hook_warn_basic_auth)
        elif default_cert is not None:
            self.cert = default_cert
        elif default_username is not None:
            self.auth = (default_username, default_password)
            self.hooks['response'].append(_hook_warn_basic_auth)
        elif fail_noauth:
            raise ValueError('No authentication credentials found.')
