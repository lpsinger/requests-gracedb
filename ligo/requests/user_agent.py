from ._version import get_versions


class SessionUserAgentMixin(object):
    """A mixin for :class:`requests.Session` to add a User-Agent header."""

    def __init__(self, *args, **kwargs):
        super(SessionUserAgentMixin, self).__init__(*args, **kwargs)
        version = get_versions()['version']
        self.headers['User-Agent'] = '{}/{}'.format(__package__, version)
