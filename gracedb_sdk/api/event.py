from os.path import join

from .base import Deletable, ChildResource
from .logs import EventLogs, SupereventLogs
from .labels import Labels


# FIXME: events have a 'log/' resource whereas superevents have 'logs/'.
# Combine BaseEvent, Event, and Superevent into a single Event class
# once this inconsistency has been fixed.
class BaseEvent(ChildResource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = self.logs_class(self)
        self.labels = Labels(self)


class Event(BaseEvent):

    logs_class = EventLogs


class Superevent(BaseEvent):

    logs_class = SupereventLogs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._events = SupereventEventList(self)

    # FIXME: GraceDB requires a random / for these URLs!
    # This is inconsistent between events and superevents.
    @property
    def url(self):
        return super().url + '/'

    def add(self, event_id):
        self._events.create(data={'event': event_id})

    def remove(self, event_id):
        self._events.delete(event_id)


class SupereventEventList(Deletable):

    path = 'events/'
