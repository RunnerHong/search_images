#!/usr/bin/env python
# @Time    : 2020/5/4 22:49
# @Author  : 洪英杰
# @Python  : 3.7.5
# @File    : feature
# @Project : search_images
# coding=utf-8
import os
import pprint

from elasticsearch import Elasticsearch, helpers
from model import Vgg16Model
import base64
import numpy as np

# http_auth = ("elastic", "123455")
# es = Elasticsearch("http://127.0.0.1:9200", http_auth=http_auth)
es = Elasticsearch("http://127.0.0.1:9200")
# images_path = '/home/runner/Pictures/search'
# images_path = '/media/runner/新加卷/school/homework/cv/BMP600'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
local_images_path = f'{BASE_DIR}/static/images/'


dfloat32 = np.dtype('>f4')


def decode_float_list(base64_string):
    bytes = base64.b64decode(base64_string)
    return np.frombuffer(bytes, dtype=dfloat32).tolist()


def encode_array(arr):
    base64_str = base64.b64encode(np.array(arr).astype(dfloat32)).decode("utf-8")
    return base64_str


body = {
  "mappings": {
    "_doc": {
      "properties": {
        "relation_id": {
          "type": "keyword" # es从2.X版本一下子跳到了5.X版本，将string类型变为了过期类型，
            # 取而代之的是text和keyword数据类型， keyword类型常常被用来过滤、排序和聚合。
        },
        "image_path": {
          "type": "keyword"
        },
        "embedding_vector": {
          "type": "binary",
          "doc_values": True
        }
      }
    }
  }
}


class Store(object):

    def __init__(self, index='index_test', images_path=local_images_path):
        self.index = index
        self.images_path = images_path

    def create_index(self):
        es.indices.create(index=self.index, body=body, include_type_name=True)

    def save_feature(self):
        listdir = os.listdir(self.images_path)
        print(listdir)
        actions = []
        try:
            for idx in listdir:
                feature = Vgg16Model().extract_feature(os.path.join(
                    self.images_path, idx)).flatten().tolist()
                feature_encode = encode_array(feature)
                action = {
                    "_op_type": "index",
                    "_index": self.index,
                    "_type": "_doc",
                    "_source": {
                                    "relation_id": idx,
                                    "embedding_vector": feature_encode,
                                    "image_path": os.path.join(
                                        self.images_path, idx)
                                }
                }
                actions.append(action)
        except BaseException as e:
            print(e)
            pass
        succeed_num = 0
        for ok, response in helpers.streaming_bulk(es, actions):
            if not ok:
                print(ok)
                print(response)
            else:
                succeed_num += 1
                print("本次更新了{0}条数据".format(succeed_num))
                es.indices.refresh('index_test')

    def search(self):
        listdir = os.listdir(self.images_path)
        print(listdir[0])
        feature = Vgg16Model().extract_feature(
            os.path.join(self.images_path, listdir[0])).flatten()
        res = es.search(index=self.index, body={
            "query": {
                "function_score": {
                    "boost_mode": "replace",
                    "script_score": {
                        "script": {
                            "source": "binary_vector_score",
                            "lang": "knn",
                            "params": {
                                "cosine": True,
                                "field": "embedding_vector",
                                "vector": feature.tolist()
                            }
                        }
                    }
                },
            },
            "_source": {
                "includes": [
                    "relation_id",
                    "image_path"
                ]
            },
            "size": 5
        })
        print("Got %d Hits:" % res['hits']['total']['value'])
        print(res['hits'])
        for hit in res['hits']['hits']:
            print(hit["_source"])
        return res

    def delete_index(self):
        es.indices.delete(self.index)
