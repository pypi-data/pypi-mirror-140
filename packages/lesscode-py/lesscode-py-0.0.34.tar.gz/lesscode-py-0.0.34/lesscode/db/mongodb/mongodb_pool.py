# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
from lesscode.db.base_connection_pool import BaseConnectionPool


class MongodbPool(BaseConnectionPool):

    """
    mongodb 数据库链接创建类
    """
    def create_pool(self):
        print("mongodb create_pool")
        """
        创建mongodb 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        info = self.conn_info
        if info.async_enable:
            import motor
            conn_info_string = f"mongodb://{info.user}:{info.password}@{info.host}:{info.port}"
            if info.params:
                if info.params == "LDAP":
                    conn_info_string += "/?authMechanism=PLAIN"
                elif info.params == "Password":
                    conn_info_string += "/?authSource=admin"
                elif info.params == "X509":
                    conn_info_string += "/?authMechanism=MONGODB-X509"
            pool = motor.motor_tornado.MotorClient(conn_info_string)
            return pool
        else:
            raise NotImplementedError
