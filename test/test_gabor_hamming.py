#!/usr/bin/env python
# @Time    : --
# @Author  : 洪英杰
# @Python  : 3.7.5
# @File    : 000_gabor_match.py
# @Project : cv
# -*- coding: utf-8 -*-
from skimage import filters, color, io
from scipy.spatial import distance
import numpy as np
from multiprocessing import Process, Manager


def get_image_feature(path):
    """
    frequency为正弦函数的频率,sigma_x/sigma_y为Gaussian 包络的标准差,
    theta为控制函数的方向.由于掌纹方向单一,令theta=O,
    取frequency=0.0916,sigma_x/sigma_y=5.6179
    参考文档： https://www.w3cschool.cn/doc_scikit_image/scikit_image-api-skimage-filters.html
    :param path: 图片路径
    :return:
    """
    img = color.rgb2gray(io.imread(path))
    real, imag = filters.gabor(
        img, frequency=0.0916, sigma_x=5.6179, sigma_y=5.6179, theta=0)
    return imag


def get_min_hamming_distance(feat0, feat1):
    # 平移实现，正数表示右移，axis=1 表示 X 轴
    min_distance = np.inf

    def calc(f0, f1):                                                       # 计算给定两个数组的汉明距离
        nonlocal min_distance
        dist = distance.hamming(f0.flatten(), f1.flatten())
        min_distance = dist if dist < min_distance else min_distance        # 存储最小的汉明距离

    calc(feat0, feat1)
    for px in range(-2,0):
        # X 左移
        temp_feats0 = np.roll(feat0, px, axis=1)[:,:px]                     # axis = 1 为横向平移
        temp_feats1 = feat1[:,:px]
        calc(temp_feats0, temp_feats1)
        # X 右移
        temp_feats1 = np.roll(feat1, px, axis=1)[:,:px]
        temp_feats0 = feat0[:,:px]
        calc(temp_feats0, temp_feats1)
        # Y 上移
        temp_feats0 = np.roll(feat0, px, axis=0)[:px,:]                     # axis = 0 为纵向平移
        temp_feats1 = feat1[:px,:]
        calc(temp_feats0, temp_feats1)
        # Y 下移
        temp_feats1 = np.roll(feat1, px, axis=0)[:px,:]
        temp_feats0 = feat0[:px,:]
        calc(temp_feats0, temp_feats1)
    return min_distance


def match_accuracy_rate(
        i, test_image_feature, pool_images_feature, pool_images,
        accuracy_rate_list, accuracy_standard):
    """
    用来匹配图片并计算匹配准确率
    :param i: 测试图片编号
    :param test_image_feature: 测试图片特征
    :param pool_images_feature: 资源图片特征池
    :param pool_images: 资源图片池
    :param accuracy_rate_list: 用于储存各个进程间的图片的匹配正确率，好汇总取平均。
    :param accuracy_standard: 匹配正确的标准，这里分为3个标准，
        1： 查找与当前图片特征最相似的5个样本，这5个样本中，每对一个，count加1，accuracy_rate=count/5。
        2：查找与当前图片特征最相似的5个样本，这5个样本中，如果正确数大于等于3，accuracy_rate=1，否则为0。
        3：单地查找与当前图片特征最相似的1个样本，如果正确，accuracy_rate=1，否则为0。
    :return:
    """
    # 汉明在误差检测与校正码的基础性论文中首次引入这个概念，这个距离，
    # 是指两个等长字符串之间的汉明距离是两个字符串对应位置的不同字符的个数。
    dists = []
    for pool_image_feature in pool_images_feature:
        # accuracy_standard == 1, avg_abccuracy_rate = 0.6859999999999998
        # accuracy_standard == 2, avg_accuracy_rate = 0.67
        # accuracy_standard == 3, avg_accuracy_rate = 0.95
        # dist = distance.hamming(
        #     test_image_feature.flatten(), pool_image_feature.flatten())
        # accuracy_standard == 1, avg_accuracy_rate = 0.83
        # accuracy_standard == 2, avg_accuracy_rate = 0.89
        # accuracy_standard == 3, avg_accuracy_rate = 0.98
        dist = get_min_hamming_distance(
            test_image_feature, pool_image_feature)
        dists.append(dist)
    dist_index = np.argsort(dists)  # 距离从小到大排列（即匹配度从大到小排列）
    count = 0
    # print(dists[dist_index[-1]])
    # 取前五个匹配度较高的图像计算匹配正确率
    for index in dist_index[:5]:
        if i < 10:
            flag = f'00{i}'
        elif i < 100:
            flag = f'0{i}'
        else:
            flag = f'{i}'
        if flag in pool_images[index]:
            count += 1
        if accuracy_standard not in [1, 2]:
            break
    if accuracy_standard == 1:
        accuracy_rate = count / 5
    elif accuracy_standard == 2:
        if count >= 3:
            accuracy_rate = 1
        else:
            accuracy_rate = 0
    else:
        accuracy_rate = count / 1
    accuracy_rate_list.append(accuracy_rate)
    return accuracy_rate_list


def image_feature_generator(
        m, n, pool_images, test_images_feature, pool_images_feature):
    """
    图片特征生成器
    :param m: 用于分割数据，便于多进程
    :param n: 用于分割数据，便于多进程
    :param pool_images: 资源图片路径池
    :param test_images_feature: 测试图片特征池
    :param pool_images_feature: 资源图片特征池
    :return:
    """
    for i in range(m, n):
        for j in range(1, 7):
            if i < 10:
                path = f'../static/images/00{i}_{j}.bmp'
            elif i < 100:
                path = f'../static/images/0{i}_{j}.bmp'
            else:
                path = f'../static/images/{i}_{j}.bmp'
            feature = get_image_feature(path)
            if j == 1:
                test_images_feature[i*10 + j] = feature
            else:
                pool_images[i*10 + j] = path
                pool_images_feature[i*10 + j] = feature


def main():
    """ 100类图片，每类图片取一张作为待匹配的图片，剩下的图片作为资源图片池，
    从中检索出与之同一类的图片，并计算正确率 """
    manager = Manager()
    accuracy_rate_list = manager.list()
    test_images_feature = manager.dict()
    pool_images_feature = manager.dict()
    pool_images = manager.dict()
    # 图片数据个数，只取整十数，如89,算80个，81,也算80个。
    k = 100
    # 多进程生成图片特征
    jobs = []
    for i in range(1, k, 10):
        m = i
        n = m + 10
        p = Process(
            target=image_feature_generator, args=(
                m, n, pool_images, test_images_feature, pool_images_feature))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()

    # 多进程，顺序乱掉了不对应，重新调整下。
    test_images_feature = dict(sorted(test_images_feature.items(),
                                      key=lambda item: item[0])).values()
    pool_images_feature = dict(sorted(pool_images_feature.items(),
                                      key=lambda item: item[0])).values()
    pool_images = list(dict(sorted(pool_images.items(),
                                   key=lambda item: item[0])).values())

    # 多进程图片匹配，并计算正确率。
    jobs = []
    accuracy_standard = 2
    for i, feature in enumerate(test_images_feature):
        p = Process(
            target=match_accuracy_rate, args=(
                i+1, feature, pool_images_feature, pool_images,
                accuracy_rate_list, accuracy_standard))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()

    avg_accuracy_rate = sum(accuracy_rate_list) / len(accuracy_rate_list)
    print(avg_accuracy_rate)  # 正确率 0.87


if __name__ == '__main__':
    main()
