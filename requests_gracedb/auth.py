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
from os import access, environ, getuid, R_OK
from os.path import expanduser, join
from six.moves.urllib.parse import urlparse

from safe_netrc import netrc

from .cert_reload import CertReloadingHTTPAdapter


def _find_cert():
    """Try to find a user's X509 certificate and key.

    Checks environment variables first, then expected location for default
    proxy.

    Notes
    -----
    This function is adapted from the original ``_find_x509_credentials()``
    method in https://git.ligo.org/lscsoft/gracedb-client/blob/gracedb-2.5.0/ligo/gracedb/
    rest.py, which is copyright (C) Brian Moe, Branson Stephens (2015).

    """  # noqa: E501
    result = tuple(environ.get(key)
                   for key in ('X509_USER_CERT', 'X509_USER_KEY'))
    if all(result):
        return result

    result = environ.get('X509_USER_PROXY')
    if result:
        return result

    result = join('/tmp', 'x509up_u{}'.format(getuid()))
    if access(result, R_OK):
        return result

    result = tuple(expanduser(join('~', '.globus', filename))
                   for filename in ('usercert.pem', 'userkey.pem'))
    if all(access(path, R_OK) for path in result):
        return result


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
            numeric user ID, if the file exists and is readable
        d.  the files :file:`~/.globus/usercert.pem` and
            :file:`~/.globus/userkey.pem`, if they exist and are readable

    5.  Read the netrc file [1]_ located at :file:`~/.netrc`, or at the path
        stored in the environment variable :envvar:`NETRC`, and look for a
        username and password matching the hostname in the URL.

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
        default_cert = _find_cert()
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
