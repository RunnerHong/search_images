#!/usr/bin/env python
# @Time    : 2020/5/13 11:46
# @Author  : 洪英杰
# @Python  : 3.7.5
# @File    : test_vgg16
# @Project : search_images
import math
import time
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Manager, cpu_count, Process

from store import Store

db = Store(model_name='vgg16')


def test_vgg16_by_thread_pool():
    search_paths = get_search_paths()
    pool = ThreadPoolExecutor(max_workers=12)
    start = time.time()
    result = list(pool.map(count_right_by_path, search_paths))
    end = time.time()
    print(sum(result) / 100)  # 准确率0.99
    print('使用多线程--timestamp:{:.3f}'.format(end-start))  # 83.691


def test_vgg16_by_process_pool():
    search_paths = get_search_paths()
    pool = ProcessPoolExecutor(max_workers=12)
    start = time.time()
    result = list(pool.map(count_right_by_path, search_paths))
    end = time.time()
    print(sum(result) / 100)  # 准确率0.99
    print('使用多进程程--timestamp:{:.3f}'.format(end-start))  # 130.886


def count_right_by_path(path):
    res = db.search(f'../static/images/{path}', size=6)
    count = 0
    print(path[0: 3])
    for hit in res['hits']['hits']:
        if path[0: 3] in hit["_source"]["relation_id"]:
            count += 1
    if count >= 4:
        return 1
    else:
        return 0


def get_search_paths():
    search_paths = []
    for i in range(1, 101):
        if len(str(i)) == 1:
            search_paths.append(f'00{i}_1.bmp')
        elif len(str(i)) == 2:
            search_paths.append(f'0{i}_1.bmp')
        elif len(str(i)) == 3:
            search_paths.append(f'{i}_1.bmp')
    return search_paths


def test_vgg16():
    search_paths = get_search_paths()
    result = Manager().list()
    split = math.ceil(len(search_paths) / cpu_count())
    jobs = []
    start = time.time()
    for i in range(0, len(search_paths), split):
        p = Process(target=count_right, args=(search_paths[i: i+split], result))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    end = time.time()
    print(sum(result) / 100)  # 准确率0.99
    print('使用共享list多进程程--timestamp:{:.3f}'.format(end-start))  # 74.461s


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
    test_vgg16()  # 74.461s
    # test_vgg16_by_thread_pool() # 83.691s
    # test_vgg16_by_process_pool()  # 130.886s
