from ._version import get_versions


class SessionUserAgentMixin:
    """A mixin for :class:`requests.Session` to add a User-Agent header."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        version = get_versions()['version']
        self.headers['User-Agent'] = f'{__package__}/{version}'
