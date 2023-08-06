# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
from lesscode.db.base_connection_pool import BaseConnectionPool
from elasticsearch import AsyncElasticsearch


class ElasticsearchPool(BaseConnectionPool):

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
            host_str = info.host.split(",")
            hosts = [f"{info.user}:{info.password}@{host}:{info.port}" for host in host_str]
            pool = AsyncElasticsearch(hosts=hosts)
            return pool
        else:
            raise NotImplementedError
