from .base import ChildResource, HasChildResources


class File(ChildResource):

    def get(self):
        return self.client.get(self.url, stream=True).raw


class Files(HasChildResources):

    path = 'files/'
    child_class = File
