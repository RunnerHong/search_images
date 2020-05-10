#!/usr/bin/env python
# @Time    : 2020/5/4 22:49
# @Author  : 洪英杰
# @Python  : 3.7.5
# @File    : train
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
images_path = '/media/runner/新加卷/school/homework/cv/BMP600'


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


def craete():
    es.indices.create(index='index_test', body=body, include_type_name=True)


def train_image_feature():
    listdir = os.listdir(images_path)
    print(listdir)
    actions = []
    try:
        for idx in listdir:
            # feature = extract_feature(model, os.path.join(images_path, idx)).tolist()
            feature = Vgg16Model().extract_feature(os.path.join(
                images_path, idx)).flatten().tolist()
            # print(feature)
            feature_encode = encode_array(feature)
            action = {
                "_op_type": "index",
                "_index": 'index_test',
                "_type": "_doc",
                "_source": {
                                "relation_id": idx,
                                "embedding_vector": feature_encode,
                                "image_path": os.path.join(images_path, idx)
                            }
            }
            actions.append(action)
    except BaseException as e:
        # print("id:{0}的图片{1}未能获取到特征".format(id, full_photo))
        # continue
        print(e)
        pass
    # print(actions)
    succeed_num = 0
    for ok, response in helpers.streaming_bulk(es, actions):
        if not ok:
            print(ok)
            print(response)
        else:
            succeed_num += 1
            print("本次更新了{0}条数据".format(succeed_num))
            es.indices.refresh('index_test')


def search():
    # res = es.search(index='index_test', size=2, body = {
    #     "query": {
    #         "match_all": {}
    #     }
    # })
    listdir = os.listdir(images_path)
    print(listdir[0])
    # feature = extract_feature(model, os.path.join(images_path, listdir[0])).flatten()
    feature = Vgg16Model().extract_feature(os.path.join(images_path, listdir[0])).flatten()
    res = es.search(index='index_test', body={
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
    # for re in res:
        # pprint.pprint(re[3])
    print("Got %d Hits:" % res['hits']['total']['value'])
    print(res['hits'])
    for hit in res['hits']['hits']:
        print(hit["_source"])


def delete():
    es.indices.delete('index_test')

# craete()
# train_image_feature()
search()
# delete()

