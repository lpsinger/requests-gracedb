from .base import Deletable


class Labels(Deletable):

    path = 'labels/'

    def create(self, label):
        return super().create_or_update(label)

    def get(self, **kwargs):
        return super().get(**kwargs)['labels']
