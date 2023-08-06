# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/26 3:56 下午
# Copyright (C) 2021 The lesscode Team
from tornado.options import options

import logging
import traceback

from neo4j import GraphDatabase, WorkspaceConfig

from lesscode.utils.aes import AES


class Neo4jHelper:

    """
    Neo4j   数据库操作实现
    """
    def __init__(self, pool):
        """
        初始化sql工具
        :param pool: 连接池名称
        """
        if isinstance(pool, str):
            self.pool, self.dialect = options.database[pool]
        else:
            self.pool = pool
            
    def __repr__(self):
        printer = 'o(>﹏<)o ......Neo4j old driver "{0}" carry me fly...... o(^o^)o'.format(self.pool)
        return printer

    def listreader(self, cypher, keys):
        """
        Read data from Neo4j in specified cypher.
        Read and parse data straightly from cypher field result.
        :param cypher: string
            Valid query cypher statement.
        :param keys: list
            Cypher query columns to return.
        :return: list
            Each returned record constructs a list and stored in a big list, [[...], [...], ...].
        """
        with self.pool.session() as session:
            with session.begin_transaction() as tx:
                data = []
                result = tx.run(cypher)
                for record in result:
                    rows = []
                    for key in keys:
                        rows.append(record[key])
                    data.append(rows)
            return data

    def dictreader(self, cypher):
        """
        Read data from Neo4j in specified cypher.
        The function depends on constructing dict method of dict(key = value) and any error may occur if the "key" is invalid to Python.
        you can choose function dictreaderopted() below to read data by hand(via the args "keys").
        :param cypher: string
            Valid query cypher statement.
        :return: list
            Each returned record constructs a dict in "key : value" pairs and stored in a big list, [{...}, {...}, ...].
        """
        with self.pool.session() as session:
            with session.begin_transaction() as tx:
                data = []
                for record in tx.run(cypher).records():
                    item = {}
                    for args in str(record).split('>')[0].split()[1:]:
                        exec
                        "item.update(dict({0}))".format(args)
                    data.append(item)
                return data

    def dictreaderopted(self, cypher, keys=None):
        """
        Optimized function of dictreader().
        Read and parse data straightly from cypher field result.
        :param cypher: string
            Valid query cypher statement.
        :param keys: list, default : none(call dictreader())
            Cypher query columns to return.
        :return: list.
            Each returned record constructs an dict in "key : value" pairs and stored in a list, [{...}, {...}, ...].
        """
        if not keys:
            return self.dictreader(cypher)
        else:
            with self.pool.session() as session:
                with session.begin_transaction() as tx:
                    data = []
                    result = tx.run(cypher)
                    for record in result:
                        item = {}
                        for key in keys:
                            item.update({key: record[key]})
                        data.append(item)
                    return data

    def cypherexecuter(self, cypher):
        """
        Execute manipulation into Neo4j in specified cypher.
        :param cypher: string
            Valid handle cypher statement.
        :return: none.
        """
        with self.pool.session() as session:
            with session.begin_transaction() as tx:
                tx.run(cypher)
        session.close()

    def parse_relation_data(cql, result_list, id_key="id", name_key="name", database="neo4j"):
        data = []
        num = 0
        stock_strike = True
        while stock_strike and num < 3:
            try:
                # neo4j_handler = Neo4jHandler(GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)))
                WorkspaceConfig.database = database
                res = cql.listreader(result_list)
                for item in res:
                    level = 1
                    if len(item) > 1:
                        if isinstance(item[1], list):
                            for item_item in item[1]:
                                relation_item = parse_relation_item(item_item, id_key, name_key, level)
                                level = level + 1
                                data.append(relation_item)
                        else:
                            relation_item = parse_relation_item(item[1], id_key, name_key, level)
                            data.append(relation_item)
                    else:
                        if isinstance(item[0], list):
                            for item_item in item[0]:
                                relation_item_list = parse_relation_item_more_relation(item_item, id_key, name_key)
                                data = data + relation_item_list
                        else:
                            relation_item_list = parse_relation_item_more_relation(item[0], id_key, name_key)
                            data = data + relation_item_list
                WorkspaceConfig.database = None
                stock_strike = False
            except Exception:
                logging.error(traceback.format_exc())
            num = num + 1
        return data

def parse_relation_item(item, id_key, name_key, level=0):
    relation_item = {"start_node": parse_node_dict(item.start_node, id_key, name_key),
                     "end_node": parse_node_dict(item.end_node, id_key, name_key),
                     "type": item.type, "level": level, "properties": item._properties}
    return relation_item

def parse_relation_item_more_relation(item, id_key, name_key):
    relation_item_list = []
    for data in item._relationships:
        relation_item_list.append(parse_relation_item(data, id_key, name_key))
    return relation_item_list

def parse_node_dict(node, id_key, name_key):
    return {
        "id": AES.encrypt(options.aes_key,node._properties[id_key]),
        "name": node._properties[name_key],
        "label": list(node._labels)[0]
    }
