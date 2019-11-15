from .base import Deletable


# FIXME: events have a 'tag/' resource whereas superevents have 'tags/'.
# Combine BaseTags, EventTags, and SupereventTags into a single Log class
# once this inconsistency has been fixed.
#
# FIXME: GraceDB expects different HTTP methods to write tags for events vs.
# superevents!
class BaseTags(Deletable):

    def get(self, **kwargs):
        return super().get(**kwargs)['tags']


class EventTags(BaseTags):

    path = 'tag/'

    def create(self, tag):
        return super().create_or_update(tag)


class SupereventTags(BaseTags):

    path = 'tags/'

    def create(self, label):
        return super().create_or_update(None, data={'name': label})
