# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
from lesscode.db.base_connection_pool import BaseConnectionPool
from aiopg import create_pool


class PostgresqlPool(BaseConnectionPool):

    """
    Postgresql 数据库链接创建类
    """
    async def create_pool(self):
        print("Postgresql create_pool")
        """
        创建postgresql 异步连接池
        :param conn_info: 连接信息
        :return: AsyncConnectionPool
        """
        info = self.conn_info
        if info.async_enable:
            pool = await create_pool(host=info.host, port=info.port, user=info.user,
                                     password=info.password,
                                     database=info.db_name)
            return pool
        else:
            raise NotImplementedError
