from .base import Resource
from .tags import EventTags, SupereventTags


# FIXME: events have a 'log/' resource whereas superevents have 'logs/'.
# Combine BaseLog, EventLog, and SupereventLog into a single Log class
# once this inconsistency has been fixed.
class BaseLog(Resource):

    def __init__(self, parent, path):
        super().__init__(parent)
        self.path = path
        self.tags = self.tags_class(self)


class EventLog(BaseLog):

    tags_class = EventTags


class SupereventLog(BaseLog):

    tags_class = SupereventTags
