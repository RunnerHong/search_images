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

3、python app.py

4、打开 http://127.0.0.1:5000/ ，然后进行测试

## 示例
todo