from abc import ABCMeta, abstractmethod


class BaseStorage(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, prefix_key):
        self.prefix_key = prefix_key + ":" if prefix_key else ""

    @abstractmethod
    async def get(self, key):
        pass

    @abstractmethod
    async def set(self, key, value):
        pass

    @abstractmethod
    async def delete(self, key):
        pass

    @abstractmethod
    async def setex(self, key, value, ttl):
        pass

    @abstractmethod
    async def hget(self, key, hashKey):
        pass

    @abstractmethod
    async def hset(self, key, hashKey, value):
        pass

    @abstractmethod
    async def hgetall(self, key):
        pass
