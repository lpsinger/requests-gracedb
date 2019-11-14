"""GraceDB API endpoints."""
from os.path import join

__all__ = ('API',)


def str_or_collection(values):
    if values is None:
        values = []
    elif isinstance(values, str):
        values = [values]
    return values


def field_collection(key, values):
    return [(key, value) for value in str_or_collection(values)]


class Resource:

    def __init__(self, parent=None):
        self.client = parent.client
        self.parent = parent

    @property
    def url(self):
        return join(self.parent.url, self.path)

    def create_or_update(self, key, **kwargs):
        if key is None:
            return self.client.post(self.url, **kwargs).json()
        else:
            self.client.put(join(self.url, key), **kwargs)

    def create(self, **kwargs):
        return self.create_or_update(None, **kwargs)

    def update(self, key, **kwargs):
        return self.create_or_update(key, **kwargs)

    def get(self, **kwargs):
        return self.client.get(self.url, **kwargs).json()


class Log(Resource):

    path = 'log/'

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


class Event(Resource):

    def __init__(self, parent, path):
        super().__init__(parent)
        self.path = path
        self.log = Log(self)


class BaseEvents(Resource):

    def __getitem__(self, key):
        return Event(self, key)

    def search(self, **kwargs):
        url = self.url
        while url:
            response = self.client.get(url, params=kwargs).json()
            url = response.get('links', {}).get('next')
            kwargs = None
            yield from response.get('events', [])


class Events(BaseEvents):

    path = 'events/'

    def create_or_update(self, event_id,
                         filename=None, filecontents=None, labels=None,
                         **kwargs):
        data = (*field_collection('labels', labels), *kwargs.items())
        files = {'eventFile': (filename, filecontents)}
        return super().create_or_update(event_id, data=data, files=files)


class Superevents(BaseEvents):

    path = 'superevents/'

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


class API:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = self
        self.events = Events(self)
        self.superevents = Superevents(self)
