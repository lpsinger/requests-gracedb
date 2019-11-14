from .base import Resource


# FIXME: events have a 'tag/' resource whereas superevents have 'tags/'.
# Combine BaseTags, EventTags, and SupereventTags into a single Log class
# once this inconsistency has been fixed.
class BaseTags(Resource):

    def create(self, tag):
        return super().create_or_update(tag)

    def get(self, **kwargs):
        return super().get(**kwargs)['tags']


class EventTags(BaseTags):

    path = 'tag/'


class SupereventTags(BaseTags):

    path = 'tags/'
