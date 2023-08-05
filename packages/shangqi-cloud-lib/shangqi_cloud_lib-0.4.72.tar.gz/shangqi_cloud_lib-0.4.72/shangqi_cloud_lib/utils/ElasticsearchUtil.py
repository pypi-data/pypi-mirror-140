import json
import logging
import os

from datetime import datetime, timedelta
import random

import requests
from elasticsearch6 import Elasticsearch
from requests.auth import HTTPBasicAuth
from shangqi_cloud_lib.context import config
from shangqi_cloud_lib.utils.AesUtil import encrypt_oracle, decrypt_oralce


def elasticsearch_connect(time_out=10000):
    if config.es_cluster_list:
        es_client = Elasticsearch(
            config.es_cluster_list,
            http_auth=(config.es_user, config.es_password),
            sniff_on_start=False,
            time_out=time_out
        )
    else:
        es_client = Elasticsearch(
            [{'host': config.es_ip, 'port': 9210}, ],
            http_auth=(config.es_user, config.es_password),
            sniff_on_start=False,
            time_out=time_out
        )

    return es_client


def es_selector_way(url_func_str, param_dict, find_condition):
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
                res = format_es_post(url, find_condition)
                flag = False
            except:
                index = index + 1
    else:
        url = url_func_str(**param_dict)
        res = format_es_post(url, find_condition)
    return res


def format_es_post(url, find_condition):
    r = requests.post(
        url,
        data=json.dumps(find_condition),
        headers={'content-type': "application/json"},
        auth=HTTPBasicAuth(config.es_user, config.es_password)
    )
    res = r.json()
    return res


def format_scroll_url(es_ip=None, es_port=None, route_key=None, scroll=None):
    return "http://{}:{}/{}/_search?scroll={}".format(es_ip if es_ip else config.es_ip,
                                                      es_port if es_port else config.es_port, route_key, scroll)


def format_scroll_id_url(es_ip=None, es_port=None):
    return "http://{}:{}/_search/scroll".format(es_ip if es_ip else config.es_ip,
                                                es_port if es_port else config.es_port)


def format_es_post_url(es_ip=None, es_port=None, route_key=None):
    return "http://{}:{}/{}/_search".format(es_ip if es_ip else config.es_ip,
                                            es_port if es_port else config.es_port, route_key)


def send_es_post(bool_must_list=None, param_list=None, route_key="", sort_list=None, size=10,
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


def format_es_return(bool_must_list=None, param_list=None, route_key="", sort_list=None, size=10, offset=0,
                     track_total_hits=False, is_need_es_score=False, is_need_decrypt_oralce=False, res=None):
    if not res:
        res = send_es_post(bool_must_list, param_list, route_key=route_key, sort_list=sort_list,
                           size=size,
                           offset=offset,
                           track_total_hits=track_total_hits)

    result_list = []
    for r in res["hits"]:
        result_list.append(format_es_param_result(r, param_list, is_need_decrypt_oralce, is_need_es_score, route_key))
    result_dict = {
        "data_count": res["total"]["value"],
        "data_list": result_list
    }
    return result_dict


def format_es_scan(bool_must_list=None, param_list=None, route_key="", scroll="5m", size=10000,
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

    res = es_selector_way(url_func_str=format_scroll_url, param_dict={
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
            data["_id"] = encrypt_oracle(data["_id"])
        data["_source"]["_id"] = data["_id"]
        result_list.append(data["_source"])
    while True:
        skip = skip + data_size

        res = es_selector_way(url_func_str=format_scroll_id_url, param_dict={
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


def format_company_id_en(value, route_key):
    if route_key in ["core.patent", "core.patent_lite"]:
        for data in value.get("tags", {}).get("proposer_type", []):
            if data.get("code"):
                data["code"] = encrypt_oracle(data["code"])
    elif route_key in ["core.research_institution"]:
        for data in value.get("tags", {}).get("support_unit", []):
            if data.get("id"):
                data["id"] = encrypt_oracle(data["id"])
    elif route_key in ["core.investment"]:
        for data in value.get("tags", {}).get("invest_company", []):
            if data.get("company_id"):
                data["company_id"] = encrypt_oracle(data["company_id"])


def format_es_param_result(r, param_list, is_need_decrypt_oralce, is_need_es_score, route_key):
    result_dict = {}
    format_company_id_en(r["_source"], route_key)
    if param_list:
        for key in param_list:
            value = r["_source"]
            key_list = key.split(".")
            for key in key_list:
                if isinstance(value, list):
                    if value:
                        value = [v.get(key, None) for v in value]
                elif isinstance(value, dict):
                    if value:
                        value = value.get(key, None)
                else:
                    pass
            if result_dict.get(key) is None:
                if value:
                    result_dict[key] = value
    else:
        result_dict = r["_source"]
    if is_need_decrypt_oralce:
        r["_id"] = encrypt_oracle(r["_id"])
    result_dict["_id"] = r["_id"]
    if is_need_es_score:
        result_dict["_score"] = r["_score"]
    return result_dict


def es_condition_by_match_phrase(bool_list, column, param, slop=0):
    if param:
        if isinstance(param, list):
            bool_list.append({
                "match_phrase": {
                    column: {
                        "query": param[0],
                        "slop": slop
                    }
                }
            })
        if isinstance(param, str):
            bool_list.append({
                "match_phrase": {
                    column: {
                        "query": param,
                        "slop": slop
                    }
                }
            })


def es_condition_by_match(bool_list, column, param):
    if param:
        if isinstance(param, list):
            bool_list.append({
                "match": {
                    column: {
                        "query": param[0],
                    }
                }
            })
        if isinstance(param, str):
            bool_list.append({
                "match": {
                    column: {
                        "query": param,
                    }
                }
            })


def es_condition_by_not_null(boo_must_list, column, param):
    if param:
        boo_must_list.append({
            "exists": {
                "field": column
            }
        })


def es_condition_by_range(bool_must_list, column, date_list, is_contain_end_date=False):
    if date_list:
        range_dict = {}
        if date_list[0]:
            range_dict["gte"] = date_list[0]
        if len(date_list) == 2 and date_list[1]:
            if "-" in str(date_list[1]) and is_contain_end_date:
                end = str((datetime.strptime(date_list[1], '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d"))
                range_dict["lt"] = end
            else:
                end = date_list[1]
                range_dict["lte"] = end
        if range_dict:
            bool_must_list.append({
                "range": {
                    column: range_dict
                }})


def es_condition_by_terms(bool_must_list, column, param_list, is_need_decrypt_oralce=False):
    if param_list:
        param_list = list(filter(None, param_list))
        if is_need_decrypt_oralce:
            for index, id in enumerate(param_list):
                try:
                    param_list[index] = int(decrypt_oralce(id))
                except:
                    logging.error("id转int失败--{}".format(id))
        if param_list:
            bool_must_list.append({
                "terms": {
                    column: param_list
                }})


def es_condition_by_exist(bool_must_list, param, is_exists="是"):
    if param:
        if is_exists == "是" or is_exists == "true":
            bool_must_list.append({
                "exists": {
                    "field": param
                }})
        else:
            bool_must_list.append({
                "bool": {
                    "must_not": [
                        {
                            "exists": {
                                "field": param
                            }
                        }
                    ]
                }
            })


def es_condition_by_exist_or_not(bool_must_list, param_dict):
    if param_dict:
        for key in param_dict:
            if param_dict[key] in ["是", "true"]:
                bool_must_list.append({
                    "exists": {
                        "field": key
                    }})
            else:
                bool_must_list.append({
                    "bool": {
                        "must_not": [
                            {
                                "exists": {
                                    "field": key
                                }
                            }
                        ]
                    }
                })


def es_condition_by_not_in(bool_must_list: list = None, column="", param_list=None):
    if param_list:
        bool_must_list.append({
            "bool": {
                "must_not": {
                    "terms": {
                        column: param_list
                    }}
            }
        })


def es_condition_by_geo_shape(bool_must_list: list = None, column="", polygon=None, geo_type="MultiPolygon",
                              relation="intersects"):
    if polygon:
        bool_must_list.append({
            "geo_shape": {
                column: {
                    "shape": {
                        "type": geo_type,
                        "coordinates": polygon
                    },
                    "relation": relation
                }
            }
        })


def format_bool_must_and_should(bool_must_list, bool_should_more_list):
    if bool_should_more_list:
        for bool_should in bool_should_more_list:
            bool_must_list.append({
                "bool": {
                    "should": bool_should
                }
            })


def format_bool_must_and_must_not(bool_must_list, bool_must_not_more_list):
    if bool_must_not_more_list:
        for bool_must_not in bool_must_not_more_list:
            bool_must_list.append({
                "bool": {
                    "must_not": bool_must_not
                }
            })


def parse_es_sort_list(column, order):
    if order == "asc":
        sort_list = [
            {
                column: {
                    "order": order,
                    "missing": "_last"
                }
            }
        ]
    else:
        sort_list = [
            {
                column: {
                    "order": order,
                    "missing": "_last"
                }
            }
        ]

    return sort_list
