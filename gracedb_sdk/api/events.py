from .base import HasChildResources
from .event import Event, Superevent
from .util import field_collection


class BaseEvents(HasChildResources):

    def search(self, **kwargs):
        url = self.url
        while url:
            response = self.client.get(url, params=kwargs).json()
            url = response.get('links', {}).get('next')
            kwargs = None
            yield from response.get('events', [])


class Events(BaseEvents):

    path = 'events/'
    child_class = Event

    def create_or_update(self, event_id,
                         filename=None, filecontents=None, labels=None,
                         **kwargs):
        data = (*field_collection('labels', labels), *kwargs.items())
        files = {'eventFile': (filename, filecontents)}
        return super().create_or_update(event_id, data=data, files=files)


class Superevents(BaseEvents):

    path = 'superevents/'
    child_class = Superevent

    def create_or_update(self, superevent_id,
                         events=None, labels=None, **kwargs):
        data = (*field_collection('events', events),
                *field_collection('labels', labels),
                *kwargs.items())
        if 'preferred_event' in kwargs:
            category_map = {'M': 'M', 'T': 'T', 'G': 'P'}
            category = category_map[kwargs['preferred_event'][0]]
            data += (('category', category),)
        return super().create_or_update(superevent_id, data=data)
