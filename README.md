# search_images
search images by one image

## 本人开发环境配置：
1、Ubuntu 18.04

2、安装elasticsearch7.5.0， https://www.elastic.co/cn/downloads/elasticsearch
 或 https://blog.csdn.net/weixin_37281289/article/details/101483434

3、安装插件fast-elasticsearch-vector-scoring7.5.0， https://github.com/lior-k/fast-elasticsearch-vector-scoring

4、python 3.7.5

## 运行：
1、启动elasticsearch

2、将图片放入/static/images/中，然后跑python3 migrate.py进行建库与保存图片特征

3、python3 app.py

4、打开 http://127.0.0.1:5000/ ，然后进行测试

## 示例
todo: add test_url

## 准确率结果
五中三以上（100类图片，每类6张，每类一张去找其它五张，三张对，才算对。）：

densenet121: 0.88  (使用共享list多进程--timestamp:321.238)

vgg16: 0.99 (使用共享list多进程--timestamp:74.461s)

resnet50: 0.61 (使用共享list多进程--timestamp:174.080s)

感觉应该是哪里出问题了，理论上densenet121会优于resnet50优于vgg16
，但结果却不是这样。难道是因为densenet121与resnet50输出的特征量少，不易区分，
因为我是用相识的图片去测试。