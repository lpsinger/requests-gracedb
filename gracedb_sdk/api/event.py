from .base import Deletable, ChildResource
from .files import Files
from .voevents import EventVOEvents, SupereventVOEvents
from .logs import EventLogs, SupereventLogs
from .labels import EventLabels, SupereventLabels


# FIXME: events have a 'log/' resource whereas superevents have 'logs/'.
# Combine BaseEvent, Event, and Superevent into a single Event class
# once this inconsistency has been fixed.
class BaseEvent(ChildResource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = Files(self)
        self.logs = self.logs_class(self)
        self.labels = self.labels_class(self)
        self.voevents = self.voevent_class(self)


class Event(BaseEvent):

    labels_class = EventLabels
    logs_class = EventLogs
    voevent_class = EventVOEvents


class Superevent(BaseEvent):

    labels_class = SupereventLabels
    logs_class = SupereventLogs
    voevent_class = SupereventVOEvents

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
