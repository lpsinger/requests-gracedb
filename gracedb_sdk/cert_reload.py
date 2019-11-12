"""HTTPS adapter to close connections with expired client certificates."""
from datetime import datetime, timedelta
from functools import partial

from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from requests.adapters import HTTPAdapter

_backend = default_backend()

__all__ = ('CertReloadingHTTPAdapter',)


def load_certificate(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    return load_pem_x509_certificate(data, _backend)


class CertReloadingHTTPSConnection(HTTPSConnection):

    def __init__(self, *args, cert_reload_timeout=timedelta(0), **kwargs):
        super().__init__(*args, **kwargs)
        self._not_valid_after = datetime.max
        self._reload_timeout = cert_reload_timeout

    @property
    def cert_has_expired(self):
        expires = self._not_valid_after - datetime.utcnow()
        return expires <= self._reload_timeout

    def connect(self):
        if self.cert_file:
            cert = load_certificate(self.cert_file)
            self._not_valid_after = cert.not_valid_after
        super().connect()


class CertReloadingHTTPSConnectionPool(HTTPSConnectionPool):

    ConnectionCls = CertReloadingHTTPSConnection

    def __init__(self, *args, cert_reload_timeout=timedelta(0), **kwargs):
        super().__init__(*args, **kwargs)
        self.conn_kw['cert_reload_timeout'] = cert_reload_timeout

    def _get_conn(self, timeout=None):
        while True:
            conn = super()._get_conn(timeout)
            # Note: this loop is guaranteed to terminate because, even if the
            # pool is completely drained, when we create a new connection, its
            # `_not_valid_after` property is set to `datetime.max`, and the
            # condition below will evaulate to `True`.
            if not conn.cert_has_expired:
                return conn


class CertReloadingHTTPAdapter(HTTPAdapter):

    def __init__(self, *args, cert_reload_timeout=0, **kwargs):
        super().__init__(*args, **kwargs)
        https_pool_cls = partial(
            CertReloadingHTTPSConnectionPool,
            cert_reload_timeout=timedelta(seconds=cert_reload_timeout))
        self.poolmanager.pool_classes_by_scheme = {
            'http': HTTPConnectionPool,
            'https': https_pool_cls}
