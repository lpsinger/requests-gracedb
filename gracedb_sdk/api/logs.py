from .base import HasChildResources
from .log import EventLog, SupereventLog
from .util import field_collection, str_or_collection


# FIXME: events have a 'log/' resource whereas superevents have 'logs/'.
# Combine BaseLogs, EventLogs, and SupereventLogs into a single Logs class
# once this inconsistency has been fixed.
class BaseLogs(HasChildResources):

    def get(self, **kwargs):
        return super().get(**kwargs)['log']

    def create_or_update(self, key, *,
                         filename=None, filecontents=None, tags=None,
                         **kwargs):
        data = (*field_collection('tagname', tags),
                *kwargs.items())
        # FIXME: gracedb server does not support form-encoded input
        # if there is no file!
        if filename is None and filecontents is None:
            json = {'tagname': str_or_collection(tags), **kwargs}
            data = None
            files = None
        else:
            data = (*field_collection('tagname', tags), *kwargs.items())
            json = None
            files = {'upload': (filename, filecontents)}
        return super().create_or_update(key, data=data, json=json, files=files)


class EventLogs(BaseLogs):

    path = 'log/'
    child_class = EventLog


class SupereventLogs(BaseLogs):

    path = 'logs/'
    child_class = SupereventLog
