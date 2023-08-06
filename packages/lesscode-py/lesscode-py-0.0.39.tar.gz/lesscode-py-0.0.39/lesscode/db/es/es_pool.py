# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
from lesscode.db.base_connection_pool import BaseConnectionPool


class EsPool(BaseConnectionPool):
    """
    Elasticsearch 数据库链接创建类
    """

    async def create_pool(self):
        print("Elasticsearch create_pool")
        """
        创建elasticsearch 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        info = self.conn_info
        if info.async_enable:
            # TODO 创建一个aiohttp 对象
            pool = {}
            return pool
        else:
            raise NotImplementedError

    def close(self):
        pass
