import os

from .singleton_meta import SingletonMeta


class Config(metaclass=SingletonMeta):

    def __init__(self):
        self._config = {
            'ALLOWED_HOSTS': os.getenv('ALLOWED_HOSTS').split(','),
            'ALLOWED_METHODS': os.getenv('ALLOWED_METHODS').split(','),
            'ALLOWED_HEADERS': os.getenv('ALLOWED_HEADERS').split(','),
        }

    def get(self, key):
        return self._config.get(key)

    def __getitem__(self, key):
        return self.get(key)
