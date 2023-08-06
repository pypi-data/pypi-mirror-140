import json

from aioredis import Redis

from ._json_encoder import JSONEncoder

decoder = json.JSONDecoder()


class AIORedisJSON:
    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: str, path: str, obj):
        if not isinstance(obj, (bytes, int, float)):
            obj = JSONEncoder(object_id_dict=True).encode(obj)
        return await self.redis.execute_command(*['JSON.SET', key, path, obj])

    async def get(self, key: str, path: str = '.'):
        val = await self.redis.execute_command(*['JSON.GET', key, path])
        if val:
            val = decoder.decode(val.decode('utf-8'))

        return val

    async def delete(self, key: str, path: str):
        return await self.redis.execute_command(*['JSON.DEL', key, path])

    async def objkeys(self, key: str, path: str):
        val = await self.redis.execute_command(*['JSON.OBJKEYS', key, path])
        if val:
            val = [key.decode('utf-8') for key in val]

        return val
