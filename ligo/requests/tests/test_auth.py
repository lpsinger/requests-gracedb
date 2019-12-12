"""Tests for :mod:`ligo.requests.auth`."""
from __future__ import print_function
import os
import random
import stat

import pytest

from .. import Session


def set_rwx_user(fileobj):
    """Set correct permissions for X.509 or netrc files."""
    os.fchmod(fileobj.fileno(), stat.S_IRWXU)


@pytest.fixture
def x509_cert_and_key(tmpdir):
    filenames = ('cert.pem', 'key.pem')
    filepaths = [str(tmpdir / filename) for filename in filenames]
    for filepath in filepaths:
        with open(filepath, 'wb') as f:
            set_rwx_user(f)
    return filepaths


@pytest.fixture
def x509_proxy(tmpdir):
    filename = 'proxy.pem'
    filepath = str(tmpdir / filename)
    with open(filepath, 'wb') as f:
        set_rwx_user(f)
    return filepath


def test_noauth_invalid():
    """Test setting both force_noauth=True and fail_if_noauth=True is an
    error."""
    with pytest.raises(ValueError):
        Session('https://example.org/', force_noauth=True, fail_if_noauth=True)


def test_force_noauth():
    """Test force_noauth=True."""
    client = Session('https://example.org/', username='albert.einstein',
                     password='super-secret', force_noauth=True)
    assert client.auth is None
    assert client.cert is None


@pytest.mark.parametrize('username,password', [['albert.einstein', None],
                                               [None, 'super-secret']])
def test_basic_invalid(username, password):
    """Test that providing username or password, but not both, is an error."""
    with pytest.raises(ValueError):
        Session('https://example.org/', username=username, password=password)


def test_basic_explicit():
    """Test basic auth with explicitly provided username and password."""
    client = Session('https://example.org/', username='albert.einstein',
                     password='super-secret')
    assert client.auth == ('albert.einstein', 'super-secret')
    assert client.cert is None


def test_x509_explicit(x509_cert_and_key):
    """Test X.509 auth provided explicitly."""
    x509_cert, x509_key = x509_cert_and_key
    client = Session('https://example.org/', cert=(x509_cert, x509_key))
    assert client.auth is None
    assert client.cert == (x509_cert, x509_key)


def test_x509_default_cert_key(monkeypatch, x509_cert_and_key):
    """Test X.509 auth provided through X509_USER_CERT and X509_USER_KEY."""
    x509_cert, x509_key = x509_cert_and_key
    monkeypatch.setenv('X509_USER_CERT', x509_cert)
    monkeypatch.setenv('X509_USER_KEY', x509_key)
    client = Session('https://example.org/')
    assert client.auth is None
    assert client.cert == (x509_cert, x509_key)


def test_x509_default_proxy(monkeypatch, x509_proxy):
    """Test X.509 auth provided through X509_USER_CERT and X509_USER_KEY."""
    monkeypatch.delenv('X509_USER_CERT', raising=False)
    monkeypatch.delenv('X509_USER_KEY', raising=False)
    monkeypatch.setenv('X509_USER_PROXY', x509_proxy)
    client = Session('https://example.org/')
    assert client.auth is None
    assert client.cert == x509_proxy


@pytest.fixture
def x509up_exists(monkeypatch):
    while True:
        uid = random.randint(1000, 10000000)
        filename = '/tmp/x509up_u{}'.format(uid)
        # try:
        #     with open(filename, 'xb') as f:
        #         set_rwx_user(f)
        # except FileExistsError:
        #     continue
        # else:
        #     break
        # FIXME: racier Python 2 version
        if os.path.exists(filename):
            continue
        with open(filename, 'wb') as f:
            set_rwx_user(f)
            break
    monkeypatch.setattr('ligo.requests.auth.getuid', lambda: uid)
    yield filename
    os.remove(filename)


@pytest.fixture
def x509up_does_not_exist(monkeypatch):
    while True:
        uid = random.randint(1000, 10000000)
        filename = '/tmp/x509up_u{}'.format(uid)
        if not os.path.exists(filename):
            break
    monkeypatch.setattr('ligo.requests.auth.getuid', lambda: uid)
    return filename


def test_x509_default_x509up(monkeypatch, tmpdir, x509up_exists):
    """Test X.509 auth provided through ~/.globus/user{cert,key}.pem."""
    monkeypatch.delenv('X509_USER_CERT', raising=False)
    monkeypatch.delenv('X509_USER_KEY', raising=False)
    monkeypatch.delenv('X509_USER_PROXY', raising=False)
    monkeypatch.setenv('HOME', str(tmpdir))
    client = Session('https://example.org/')
    assert client.auth is None
    assert client.cert == x509up_exists


def test_x509_default_globus(monkeypatch, tmpdir, x509up_does_not_exist):
    """Test X.509 auth provided through ~/.globus/user{cert,key}.pem."""
    monkeypatch.delenv('X509_USER_CERT', raising=False)
    monkeypatch.delenv('X509_USER_KEY', raising=False)
    monkeypatch.delenv('X509_USER_PROXY', raising=False)
    monkeypatch.setenv('HOME', str(tmpdir))
    os.mkdir(str(tmpdir / '.globus'))
    filenames = ['usercert.pem', 'userkey.pem']
    filepaths = [str(tmpdir / '.globus' / filename) for filename in filenames]
    for path in filepaths:
        with open(path, 'wb') as f:
            set_rwx_user(f)
    client = Session('https://example.org/')
    assert client.auth is None
    assert client.cert == tuple(filepaths)


def test_basic_default(monkeypatch, tmpdir, x509up_does_not_exist):
    """Test basic auth provided through a netrc file."""
    filename = str(tmpdir / 'netrc')
    with open(filename, 'w') as f:
        print('machine', 'example.org', 'login', 'albert.einstein',
              'password', 'super-secret', file=f)
        set_rwx_user(f)
    monkeypatch.setenv('NETRC', filename)
    monkeypatch.delenv('X509_USER_CERT', raising=False)
    monkeypatch.delenv('X509_USER_KEY', raising=False)
    monkeypatch.delenv('X509_USER_PROXY', raising=False)
    monkeypatch.setenv('HOME', str(tmpdir))
    client = Session('https://example.org/')
    assert client.auth == ('albert.einstein', 'super-secret')
    assert client.cert is None


def test_fail_if_noauth(monkeypatch, tmpdir, x509up_does_not_exist):
    monkeypatch.setenv('NETRC', str(tmpdir / 'netrc'))
    monkeypatch.delenv('X509_USER_CERT', raising=False)
    monkeypatch.delenv('X509_USER_KEY', raising=False)
    monkeypatch.delenv('X509_USER_PROXY', raising=False)
    monkeypatch.setenv('HOME', str(tmpdir))
    client = Session('https://example.org/')
    assert client.auth is None
    assert client.cert is None
    with pytest.raises(ValueError):
        Session('https://example.org/', fail_if_noauth=True)
