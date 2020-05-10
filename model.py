#!/usr/bin/env python
# @Time    : 2020/5/4 21:08
# @Author  : 洪英杰
# @Python  : 3.7.5
# @File    : model
# @Project : search_images
import torch
import torch.nn
import torchvision.models as models
from torch.autograd import Variable
import torch.cuda
import torchvision.transforms as transforms

from PIL import Image

TARGET_IMG_SIZE = 224
img_to_tensor = transforms.ToTensor()


class Vgg16Model(object):

    def __init__(self):
        self.model = self.make_model()

    def make_model(self):
        # 其实就是定位到第28层，对照着上面的key看就可以理解
        model = models.vgg16(pretrained=True).features[:28]
        # print(model)
        model = model.eval()  # 一定要有这行，不然运算速度会变慢（要求梯度）而且会影响结果
        if torch.cuda.is_available():
            model.cuda()  # 将模型从CPU发送到GPU,如果没有GPU则删除该行
        return model

    def extract_feature(self, imgpath):
        """
        特征提取
        :param imgpath: 图片地址
        :return:
        """
        self.model.eval()  # 必须要有，不然会影响特征提取结果

        img=Image.open(imgpath)	 # 读取图片
        img = img.convert('RGB')
        # print(img.size)
        img=img.resize((TARGET_IMG_SIZE, TARGET_IMG_SIZE))
        tensor=img_to_tensor(img)	# 将图片转化成tensor
        # RuntimeError: Expected 4-dimensional input for 4-dimensional weight 64 3 3 3,
        # but got 3-dimensional input of size [4, 224, 224] instead, so do below
        tensor = torch.unsqueeze(tensor, dim=0)
        if torch.cuda.is_available():
            tensor = tensor.cuda()  # 如果只是在cpu上跑的话要将这行去掉

        result = self.model(Variable(tensor))
        result_npy = result.data.cpu().numpy()  # 保存的时候一定要记得转成cpu形式的，不然可能会出错
        # img = Image.fromarray(result_npy[0], 'RGB')
        # img.show()
        return result_npy[0] # 返回的矩阵shape是[1, 512, 14, 14]，这么做是为了让shape变回[512, 14,14]
