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
from __future__ import absolute_import
from os.path import basename
from mimetypes import guess_type
from sys import stdin

from requests.utils import guess_filename, to_key_val_list


def _guess_content_type(filename):
    return guess_type(filename)[0] or 'application/octet-stream'


def _guess_mime_type(key, val):
    if not isinstance(val, (tuple, list)):
        filename = guess_filename(val) or key
        filetype = _guess_content_type(filename)
        val = (filename, val, filetype)
    elif len(val) < 3 or val[2] is None:
        filename = val[0]
        filetype = _guess_content_type(filename)
        # val = (*val[:2], filetype, *val[3:])
        # FIXME: Python 2
        val = tuple(val[:2]) + (filetype,) + tuple(val[3:])
    return key, val


def _read_files(key, val):
    if isinstance(val, (tuple, list)) and (len(val) < 2 or val[1] is None):
        filename = val[0]
        with (stdin.buffer if filename == '-' else open(filename, 'rb')) as f:
            data = f.read()
        filename = basename(filename)
        # val = (filename, data, *val[2:])
        # FIXME: Python 2
        val = (filename, data) + tuple(val[2:])
    return key, val


def _prepare_file(key, val):
    key, val = _read_files(key, val)
    key, val = _guess_mime_type(key, val)
    return key, val


def _prepare_files(files):
    if files is not None:
        files = [_prepare_file(k, v) for k, v in to_key_val_list(files)]
    return files


class SessionFileMixin(object):
    """A mixin for :class:`requests.Session` to add features for file uploads.

    The :meth:`requests.Session.request` method takes a `files` argument which
    is a dictionary of `{fieldname: fileobject}`, where `fileobject` may be a
    file-like object or a tuple of 2-4 elements consisting of the filename,
    file content, MIME type, and any custom headers.

    This mixin adds the following features:

    * The MIME type is automatically guessed from the filename.
    * If the file content is None, then the filename is treated as a path, and
      the file is opened and read. If the filename is `-`, then the file
      content is read from stdin.
    """

    def request(
            self, method, url, params=None, data=None, headers=None,
            cookies=None, files=None, auth=None, timeout=None,
            allow_redirects=True, proxies=None, hooks=None, stream=None,
            verify=None, cert=None, json=None):
        return super(SessionFileMixin, self).request(
            method, url, params=params, data=data, headers=headers,
            cookies=cookies, files=_prepare_files(files), auth=auth,
            timeout=timeout, allow_redirects=True, proxies=proxies,
            hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)
