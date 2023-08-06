# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
from neo4j import GraphDatabase

from lesscode.db.base_connection_pool import BaseConnectionPool
import aiomysql


class Neo4jPool(BaseConnectionPool):

    """
    mysql 数据库链接创建类
    """
    async def create_pool(self):
        """
        创建Neo4j 连接池
        :return:
        """
        if self.conn_info.async_enable:
            pool = GraphDatabase.driver(f"bolt://{self.conn_info.host}:{self.conn_info.port}", auth=(self.conn_info.user, self.conn_info.password))
                # await aiomysql.create_pool(host=self.conn_info.host, port=self.conn_info.port,
                #                               user=self.conn_info.user,
                #                               password=self.conn_info.password, pool_recycle=3600,
                #                               db=self.conn_info.db_name, autocommit=True,
                #                               minsize=self.conn_info.min_size,
                #                               maxsize=self.conn_info.max_size)
            return pool
        else:
            raise NotImplementedError
