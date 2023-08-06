import asyncio
import copy
import datetime
import inspect
import json
import logging
from typing import TYPE_CHECKING, Optional, cast

import aioredis
import jwt
from bson import ObjectId

from nawah.classes import JSONEncoder
from nawah.config import Config
from nawah.enums import Event
from nawah.utils import check_cache_connection

if TYPE_CHECKING:
    from nawah.base_module import BaseModule
    from nawah.classes import CACHE, NAWAH_ENV, NAWAH_EVENTS, NAWAH_QUERY

logger = logging.getLogger('nawah')


def _generate_cache_key(
    cache: 'CACHE',
    method: str,
    module: 'BaseModule',
    skip_events: 'NAWAH_EVENTS',
    env: 'NAWAH_ENV',
    query: 'NAWAH_QUERY',
) -> Optional[str]:
    if not Config._sys_cache or Event.CACHE in skip_events or not cache:
        return None

    condition_params = {
        'skip_events': skip_events,
        'env': env,
        'query': query,
    }

    if not cache.condition(
        **{
            param: condition_params[param]
            for param in inspect.signature(cache.condition).parameters
        }
    ):
        return None

    cache_key = {
        'query': JSONEncoder().encode(query._query),
        'special': JSONEncoder().encode(query._special),
        'extn': Event.EXTN in skip_events,
        'user': env['session']['user']['_id'] if cache.user_scoped else None,
    }

    cache_key_jwt = jwt.encode(cache_key, '_').split('.')[1]

    return cache_key_jwt


def _call_cache_decoder(cache_dict):
    if not cache_dict:
        return

    for key in cache_dict:
        if isinstance(cache_dict[key], dict):
            if '$oid' in cache_dict[key]:
                cache_dict[key] = ObjectId(cache_dict[key]['$oid'])
            else:
                _call_cache_decoder(cache_dict=cache_dict[key])
        elif isinstance(cache_dict[key], list):
            for i in range(len(cache_dict[key])):
                if isinstance(cache_dict[key][i], dict):
                    if '$oid' in cache_dict[key][i]:
                        cache_dict[key][i] = ObjectId(cache_dict[key][i]['$oid'])
                    else:
                        _call_cache_decoder(cache_dict=cache_dict[key][i])


async def _call_cache(
    cache: 'CACHE', method: str, module: 'BaseModule', cache_key: str
):
    if not Config._sys_cache:
        return

    try:
        logger.debug(
            'Attempting to get cache with \'key\': \'%s\'.',
            f'.{module.module_name}.{method}.{cache_key}',
        )

        await check_cache_connection()

        cache_dict = await Config._sys_cache.get(
            f'{cache.channel}:{module.module_name}:{method}:{cache_key}',
            f'.results',
        )

        _call_cache_decoder(cache_dict=cache_dict)

        return cache_dict

    except aioredis.exceptions.ResponseError:
        return

    except aioredis.exceptions.ConnectionError:
        logger.error(
            'Connection with Redis server \'%s\' failed. Skipping Cache Workflow.',
            Config.cache_server,
        )
        return


async def _set_cache(channel, module, method, cache_key, results):
    if not Config._sys_cache:
        return

    results = copy.deepcopy(results)

    try:
        logger.debug(
            'Attempting to set cache with \'key\': \'%s\'.',
            f'.{module}.{method}.{cache_key}',
        )

        await check_cache_connection()

        results = {
            'docs': [doc['_id'] for doc in results['args']['docs']]
            if 'args' in results and 'docs' in results['args']
            else [],
            'results': results,
        }

        await Config._sys_cache.set(
            f'{channel}:{module}:{method}:{cache_key}',
            '.',
            json.loads(JSONEncoder(object_id_dict=True).encode(results)),
        )

        if Config.cache_expiry:
            await Config._sys_cache.redis.expire(
                f'{channel}:{module}:{method}:{cache_key}', Config.cache_expiry
            )

    except aioredis.exceptions.ConnectionError:
        logger.error(
            'Connection with Redis server \'%s\' failed. Skipping Cache Workflow.',
            Config.cache_server,
        )


async def _call_method(
    cache: 'CACHE',
    method: str,
    module: 'BaseModule',
    skip_events: 'NAWAH_EVENTS',
    env: 'NAWAH_ENV',
    query: 'NAWAH_QUERY',
):
    cache_key = _generate_cache_key(
        cache=cache,
        method=method,
        module=module,
        skip_events=skip_events,
        env=env,
        query=query,
    )
    call_cache = None
    if cache_key:
        cache_key = cast(str, cache_key)
        call_cache = await _call_cache(
            cache=cache, method=method, module=module, cache_key=cache_key
        )

    async def _method(skip_events, env, query, doc):
        if call_cache:
            return call_cache

        module_method = getattr(module, f'_method_{method}')

        method_params = {
            'skip_events': skip_events,
            'env': env,
            'query': query,
            'doc': doc,
        }

        results = await module_method(
            **{
                param: method_params[param]
                for param in inspect.signature(module_method).parameters
            }
        )

        if cache_key:
            results['args']['cache_key'] = cache_key
            if 'cache_time' not in results['args']:
                logger.debug(
                    'Results generated with \'cache_key\'. Calling \'_set_cache\'.'
                )
                results['args']['cache_time'] = datetime.datetime.utcnow().isoformat()
                asyncio.create_task(
                    _set_cache(
                        cache.channel, module.module_name, method, cache_key, results
                    )
                )

        return results

    return _method
