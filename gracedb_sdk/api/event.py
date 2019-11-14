from .base import ChildResource
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
