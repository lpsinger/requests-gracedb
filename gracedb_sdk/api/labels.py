from .base import Resource


class Labels(Resource):

    path = 'labels/'

    def create(self, label):
        return super().create_or_update(label)

    def get(self, **kwargs):
        return super().get(**kwargs)['labels']
