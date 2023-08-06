# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/12/8 10:53 上午
# Copyright (C) 2021 The lesscode Team
import json
import logging
import random

import requests
from requests.auth import HTTPBasicAuth
from tornado.options import options

from lesscode.db.base_sql_helper import BaseSqlHelper, echo_sql
from lesscode.db.condition_wrapper import ConditionWrapper
from lesscode.db.page import Page
from lesscode.utils.EsUtil import format_es_param_result
from lesscode.utils.aes import AES


class EsHelper:
    """
    ElasticsearchHelper  ES数据库操作实现
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

    def es_selector_way(self,url_func_str, param_dict, find_condition):
        res = None
        # 如果有集群优先集群
        if config.es_cluster_list:
            # 随机打乱列表
            random.shuffle(config.es_cluster_list)
            index = 0
            flag = True
            while index < len(config.es_cluster_list) and flag:
                param_dict["es_ip"] = config.es_cluster_list[index]["host"]
                param_dict["es_port"] = config.es_cluster_list[index]["port"]
                url = url_func_str(**param_dict)
                try:
                    res = self.format_es_post(url, find_condition)
                    flag = False
                except:
                    index = index + 1
        else:
            url = url_func_str(**param_dict)
            res = self.format_es_post(url, find_condition)
        return res

    def format_es_post(self,url, find_condition):
        r = requests.post(
            url,
            data=json.dumps(find_condition),
            headers={'content-type': "application/json"},
            auth=HTTPBasicAuth(config.es_user, config.es_password)
        )
        res = r.json()
        return res

    def format_scroll_url(self,es_ip=None, es_port=None, route_key=None, scroll=None):
        return "http://{}:{}/{}/_search?scroll={}".format(es_ip if es_ip else config.es_ip,
                                                          es_port if es_port else config.es_port, route_key, scroll)

    def format_scroll_id_url(self,es_ip=None, es_port=None):
        return "http://{}:{}/_search/scroll".format(es_ip if es_ip else config.es_ip,
                                                    es_port if es_port else config.es_port)

    def format_es_post_url(self,es_ip=None, es_port=None, route_key=None):
        return "http://{}:{}/{}/_search".format(es_ip if es_ip else config.es_ip,
                                                es_port if es_port else config.es_port, route_key)

    def send_es_post(self,bool_must_list=None, param_list=None, route_key="", sort_list=None, size=10,
                     offset=0,
                     track_total_hits=False):
        params = {
            "query": {
                "bool": {
                    "must": bool_must_list
                }
            },
            "size": size,
            "from": offset,
        }
        if track_total_hits:
            params["track_total_hits"] = track_total_hits
        if param_list:
            params["_source"] = {"include": param_list}
        if sort_list:
            params["sort"] = sort_list
        start_time = datetime.now()

        res = es_selector_way(url_func_str=format_es_post_url, param_dict={
            "route_key": route_key,
        }, find_condition=params)
        logging.info("进程{}，路由{},查询时间{}".format(os.getpid(), route_key, datetime.now() - start_time))

        if "error" in list(res.keys()):
            logging.info(res)
        return res["hits"]

    def format_es_return(self,bool_must_list=None, param_list=None, route_key="", sort_list=None, size=10, offset=0,
                         track_total_hits=False, is_need_es_score=False, is_need_decrypt_oralce=False, res=None):
        if not res:
            res = self.send_es_post(bool_must_list, param_list, route_key=route_key, sort_list=sort_list,
                               size=size,
                               offset=offset,
                               track_total_hits=track_total_hits)

        result_list = []
        for r in res["hits"]:
            result_list.append(
                format_es_param_result(r, param_list, is_need_decrypt_oralce, is_need_es_score, route_key))
        result_dict = {
            "data_count": res["total"]["value"],
            "data_list": result_list
        }
        return result_dict

    def format_es_scan(self,bool_must_list=None, param_list=None, route_key="", scroll="5m", size=10000,
                       is_need_decrypt_oralce=False, limit=None):
        logging.info("扫描开始，条件是{},查询字段是{}".format(json.dumps(bool_must_list), json.dumps(param_list)))
        skip = 0
        request_param = {
            "query": {
                "bool": {
                    "must": bool_must_list
                }
            }
            , "size": size,

        }
        if param_list:
            request_param["_source"] = {"include": param_list}

        res = self.es_selector_way(url_func_str=self.format_scroll_url, param_dict={
            "route_key": route_key,
            "scroll": scroll
        }, find_condition=request_param)

        data_size = len(res["hits"]["hits"])
        logging.info(
            "扫描{}:{}条花费时间{}ms,".format(route_key, str(skip) + "-" + str(skip + data_size), res["took"]))
        scroll_id = res["_scroll_id"]
        result_list = []
        for data in res["hits"]["hits"]:
            if is_need_decrypt_oralce:
                data["_id"] = AES.encrypt("haohaoxuexi",data["_id"])
            data["_source"]["_id"] = data["_id"]
            result_list.append(data["_source"])
        while True:
            skip = skip + data_size

            res = self.es_selector_way(url_func_str=self.format_scroll_id_url, param_dict={
            }, find_condition={
                "scroll": scroll,
                "scroll_id": scroll_id})
            data_size = len(res["hits"]["hits"])
            logging.info("扫描{}:{}条花费时间{}ms,".format(route_key, str(skip) + "-" + str(skip + data_size), res["took"]))
            scroll_id = res.get("_scroll_id")
            # end of scroll
            if scroll_id is None or not res["hits"]["hits"]:
                break
            for data in res["hits"]["hits"]:
                data["_source"]["_id"] = data["_id"]
                result_list.append(data["_source"])
            if limit and limit <= len(result_list):
                break
        return result_list

