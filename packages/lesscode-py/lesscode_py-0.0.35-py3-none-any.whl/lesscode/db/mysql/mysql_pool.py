# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
from lesscode.db.base_connection_pool import BaseConnectionPool
import aiomysql


class MysqlPool(BaseConnectionPool):

    """
    mysql 数据库链接创建类
    """
    async def create_pool(self):
        """
        创建mysql 异步连接池
        :return:
        """
        if self.conn_info.async_enable:
            pool = await aiomysql.create_pool(host=self.conn_info.host, port=self.conn_info.port,
                                              user=self.conn_info.user,
                                              password=self.conn_info.password, pool_recycle=3600*4,
                                              db=self.conn_info.db_name, autocommit=True,
                                              minsize=self.conn_info.min_size,
                                              maxsize=self.conn_info.max_size)
            return pool
        else:
            raise NotImplementedError
