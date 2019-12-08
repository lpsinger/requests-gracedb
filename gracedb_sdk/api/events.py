from os.path import join

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
            yield from response.get(self.path.strip('/'), [])


class Events(BaseEvents):

    path = 'events/'
    child_class = Event

    def __getitem__(self, key):
        if 'S' in key:
            return self.parent.superevents[key]
        else:
            return super()[key]

    def create_or_update(self, event_id, *,
                         filename='initial.data',
                         filecontents=None, labels=None, **kwargs):
        data = (*field_collection('labels', labels), *kwargs.items())
        files = {'eventFile': (filename, filecontents)}
        return super().create_or_update(event_id, data=data, files=files)


SUPEREVENT_CATEGORIES = {'M': 'M', 'T': 'T', 'G': 'P'}


class Superevents(BaseEvents):

    path = 'superevents/'
    child_class = Superevent

    def __getitem__(self, key):
        if 'S' not in key:
            return self.parent.events[key]
        else:
            return super()[key]

    def create_or_update(self, superevent_id, *,
                         events=None, labels=None, **kwargs):
        data = (*field_collection('events', events),
                *field_collection('labels', labels),
                *kwargs.items())
        if 'preferred_event' in kwargs:
            category = SUPEREVENT_CATEGORIES[kwargs['preferred_event'][0]]
            data += (('category', category),)
        if superevent_id is None:
            return super().create_or_update(superevent_id, data=data)
        else:
            # FIXME: GraceDB does not support 'put' here, only 'patch'!
            # This is inconsistent between events and superevents.
            url = join(self.url, superevent_id) + '/'
            self.client.patch(url, data=data)
