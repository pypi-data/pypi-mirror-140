# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/26 3:56 下午
# Copyright (C) 2021 The lesscode Team
import aioredis
from tornado.options import options


class RedisHelper:

    def __init__(self, pool):
        """
        初始化sql工具
        :param pool: 连接池名称
        """
        if isinstance(pool, str):
            self.pool, self.dialect = options.database[pool]
        else:
            self.pool = pool

    def get_connection(self):
        return aioredis.Redis(connection_pool=self.pool, decode_responses=True)

    async def set(self, name, value, ex=None, px=None, nx: bool = False, xx: bool = False, keepttl: bool = False):
        await self.get_connection().set(name, value, ex, px, nx, xx, keepttl)

    async def get(self, name):
        return await self.get_connection().get(name)

    async def delete(self, names):
        if isinstance(names, list) or isinstance(names, tuple):
            await self.get_connection().delete(*names)
        else:
            await self.get_connection().delete(names)

    async def rpush(self, name, values: list, time=None):
        await self.get_connection().rpush(name, *values)
        if time:
            await self.get_connection().expire(name, time)

    async def hset(self, name, key=None, value=None, mapping=None, time=None):
        await self.get_connection().hset(name, key=key, value=value, mapping=mapping)
        if time:
            await self.get_connection().expire(name, time)

    async def hgetall(self, name):
        return await self.get_connection().hgetall(name)

    async def hget(self, name, key):
        return await self.get_connection().hget(name, key)
