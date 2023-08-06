'''Provides `reset_cache`, `reset_expired_cache` Utility'''
import logging
from typing import cast

import aioredis

from nawah.classes import AIORedisJSON
from nawah.config import Config

logger = logging.getLogger('nawah')

Config._sys_cache = cast(AIORedisJSON, Config._sys_cache)
Config.cache_expiry = cast(int, Config.cache_expiry)


async def check_cache_connection(attempt: int = 3):
    '''Attempts to read from cache to force re-connection if broken'''

    try:
        await Config._sys_cache.get('__connection')
    except aioredis.exceptions.ConnectionError as e:
        if attempt != 0:
            return await check_cache_connection(attempt=attempt - 1)

        raise e


async def reset_cache_channel(channel: str):
    '''Resets specific cache `channel` by deleting it from active Redis db'''

    await check_cache_connection()

    try:
        for key in await Config._sys_cache.redis.keys(f'{channel}:*'):
            try:
                await Config._sys_cache.redis.delete(key.decode('utf-8'))
            except aioredis.exceptions.ResponseError:
                logger.error('Failed to delete Cache Key: \'%s\'', key)
    except aioredis.exceptions.ConnectionError:
        logger.error(
            'Connection with Redis server \'%s\' failed. Skipping resetting Cache Channel \'%s\'.',
            Config.cache_server,
            channel,
        )
