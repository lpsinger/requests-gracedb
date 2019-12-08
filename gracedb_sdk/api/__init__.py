"""GraceDB API endpoints."""
from .events import Events, Superevents


class API:

    def __init__(self, url, *args, **kwargs):
        super().__init__(url, *args, **kwargs)
        self.url = url
        self.client = self
        self.events = Events(self)
        self.superevents = Superevents(self)
