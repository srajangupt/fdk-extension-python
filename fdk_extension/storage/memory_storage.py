from fdk_extension.storage.base_storage import BaseStorage


class MemoryStorage(BaseStorage):

    def __init__(self, prefix_key):
        super().__init__(prefix_key)
        self._data = {}

    async def get(self, key):
        return self._data[self.prefix_key + key]

    async def set(self, key, value):
        self._data[self.prefix_key + key] = value

    async def delete(self, key):
        del self._data[self.prefix_key + key]

    async def setex(self, key, value, ttl):
        # TODO: add support for ttl
        self._data[self.prefix_key + key] = value

    async def hget(self, key, hash_key):
        hash_map = self._data[self.prefix_key + key]
        if hash_map:
            return hash_map[hash_key]

    async def hset(self, key, hash_key, value):
        hash_map = self._data.get([self.prefix_key + key], {})
        hash_map[hash_key] = value
        self._data[self.prefix_key + key] = hash_map

    async def hgetall(self, key):
        return self._data[self.prefix_key + key]
