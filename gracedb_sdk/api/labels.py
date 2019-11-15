from .base import Deletable


# FIXME: GraceDB expects different HTTP methods to write labels for events vs.
# superevents! Replace BaseLabels, EventLabels, SupereventLabels with a single
# Labels class once this is fixed.
class BaseLabels(Deletable):

    path = 'labels/'

    def get(self, **kwargs):
        return super().get(**kwargs)['labels']


class EventLabels(BaseLabels):

    path = 'labels/'

    def create(self, label):
        return super().create_or_update(label)


class SupereventLabels(BaseLabels):

    path = 'labels/'

    def create(self, label):
        return super().create_or_update(None, data={'name': label})
