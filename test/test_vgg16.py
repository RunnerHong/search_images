#!/usr/bin/env python
# @Time    : 2020/5/13 11:46
# @Author  : 洪英杰
# @Python  : 3.7.5
# @File    : test_vgg16
# @Project : search_images
import math
from multiprocessing import Manager, cpu_count, Process

from store import Store

db = Store()


def test_vgg16():
    search_paths = []
    for i in range(1, 101):
        if len(str(i)) == 1:
            search_paths.append(f'00{i}_1.bmp')
        elif len(str(i)) == 2:
            search_paths.append(f'0{i}_1.bmp')
        elif len(str(i)) == 3:
            search_paths.append(f'{i}_1.bmp')
    result = Manager().list()
    split = math.ceil(len(search_paths) / cpu_count())
    jobs = []
    for i in range(0, len(search_paths), split):
        p = Process(target=count_right, args=(search_paths[i: i+split], result))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    print(sum(result) / 100)  # 准确率0.99


def count_right(search_paths, result):
    for path in search_paths:
        res = db.search(f'../static/images/{path}', size=6)
        count = 0
        print(path[0: 3])
        for hit in res['hits']['hits']:
            if path[0: 3] in hit["_source"]["relation_id"]:
                count += 1
        if count >= 4:
            result.append(1)
        else:
            result.append(0)


if __name__ == '__main__':
    test_vgg16()