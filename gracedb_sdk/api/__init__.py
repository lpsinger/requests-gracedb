"""GraceDB API endpoints."""
from .events import Events, Superevents


class API:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = self
        self.events = Events(self)
        self.superevents = Superevents(self)
