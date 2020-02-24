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
"""HTTPS adapter to close connections with expired client certificates."""
from __future__ import absolute_import
from datetime import datetime, timedelta
from functools import partial

from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from requests.packages.urllib3.connection import HTTPSConnection
from requests.packages.urllib3.connectionpool import (HTTPConnectionPool,
                                                      HTTPSConnectionPool)
from requests.adapters import HTTPAdapter

_backend = default_backend()


def load_x509_certificate(filename):
    """Load an X.509 certificate from a file.

    Parameters
    ----------
    filename : str
        The name of the certificate file.

    Returns
    -------
    cert : cryptography.x509.Certificate
        The parsed certificate.

    """
    with open(filename, 'rb') as f:
        data = f.read()
    return load_pem_x509_certificate(data, _backend)


class _CertReloadingHTTPSConnection(HTTPSConnection):

    def __init__(self, host, cert_reload_timeout=0, **kwargs):
        super(_CertReloadingHTTPSConnection, self).__init__(host, **kwargs)
        self._not_valid_after = datetime.max
        self._reload_timeout = timedelta(seconds=cert_reload_timeout)

    @property
    def cert_has_expired(self):
        expires = self._not_valid_after - datetime.utcnow()
        return expires <= self._reload_timeout

    def connect(self):
        if self.cert_file:
            cert = load_x509_certificate(self.cert_file)
            self._not_valid_after = cert.not_valid_after
        super(_CertReloadingHTTPSConnection, self).connect()


class _CertReloadingHTTPSConnectionPool(HTTPSConnectionPool):

    ConnectionCls = _CertReloadingHTTPSConnection

    def __init__(self, host, port=None, cert_reload_timeout=0, **kwargs):
        super(_CertReloadingHTTPSConnectionPool, self).__init__(
            host, port=port, **kwargs)
        self.conn_kw['cert_reload_timeout'] = cert_reload_timeout

    def _get_conn(self, timeout=None):
        while True:
            conn = super(_CertReloadingHTTPSConnectionPool, self)._get_conn(
                timeout)
            # Note: this loop is guaranteed to terminate because, even if the
            # pool is completely drained, when we create a new connection, its
            # `_not_valid_after` property is set to `datetime.max`, and the
            # condition below will evaulate to `True`.
            if not conn.cert_has_expired:
                return conn
            conn.close()


class CertReloadingHTTPAdapter(HTTPAdapter):
    """A mixin for :class:`requests.Session` to automatically reload the client
    X.509 certificates if the version that is stored in the session is going to
    expire soon.

    Parameters
    ----------
    cert_reload_timeout : int
        Reload the certificate if it expires within this many seconds from now.

    """

    def __init__(self, cert_reload_timeout=0, **kwargs):
        super(CertReloadingHTTPAdapter, self).__init__(**kwargs)
        https_pool_cls = partial(
            _CertReloadingHTTPSConnectionPool,
            cert_reload_timeout=cert_reload_timeout)
        self.poolmanager.pool_classes_by_scheme = {
            'http': HTTPConnectionPool,
            'https': https_pool_cls}
