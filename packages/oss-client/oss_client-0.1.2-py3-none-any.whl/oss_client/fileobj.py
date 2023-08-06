import os
from oss_client.utils import content_md5


class FileObject(object):
    def __init__(self, name="", obj=None, hash_value=None, storage=None):
        if not (obj or hash_value):
            raise ValueError("obj and hash_value both are None")
        self.obj = obj
        self.name = name
        self.suffix = ""
        self.length = 0
        self.hash_value = hash_value
        self.storage = storage
        names = name.split(".")
        if len(names) > 1:
            self.suffix = names[-1]
        if not self.hash_value and self.obj:
            content = self.obj.read()
            self.length = len(content)
            self.hash_value = content_md5(content)
            self.obj.seek(0, os.SEEK_SET)

    def __str__(self):
        return self.hash_value

    def key(self):
        return self.hash_value

    def content(self, range=None):
        if self.obj:
            return self.obj.read()
        if self.storage:
            return self.storage.read(self.key(), range)
        raise Exception("can not find content")
