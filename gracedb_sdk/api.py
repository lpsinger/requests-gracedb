"""GraceDB API endpoints."""
from os.path import join

__all__ = ('API',)


def field_collection(key, values):
    if isinstance(values, str):
        yield key, values
    elif values is not None:
        for value in values:
            yield key, value


class Resource:

    def __init__(self, parent=None):
        self.client = parent.client
        self.parent = parent

    @property
    def url(self):
        return join(self.parent.url, self.path)

    def create_or_update(self, key, *args, **kwargs):
        if key is None:
            return self.client.post(self.url, *args, **kwargs).json()
        else:
            self.client.put(join(self.url, key), *args, **kwargs)

    def create(self, *args, **kwargs):
        return self.create_or_update(None, *args, **kwargs)

    def update(self, key, *args, **kwargs):
        return self.create_or_update(key, *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.client.get(self.url, *args, **kwargs).json()


class Log(Resource):

    path = 'log/'

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)['log']

    def create_or_update(self, key,
                         message, filename=None, filecontents=None, tags=None,
                         **kwargs):
        data = (('comment', message),
                *field_collection('tagname', tags),
                *kwargs.items())
        if filename is None and filecontents is None:
            files = None
        else:
            files = {'upload': (filename, filecontents)}
        return super().create_or_update(key, data=data, files=files)


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
        return super().create_or_update(superevent_id, data=data)


class API:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = self
        self.events = Events(self)
        self.superevents = Superevents(self)
