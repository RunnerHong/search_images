#!/usr/bin/env python
# @Time    : 2020/5/10 12:55
# @Author  : 洪英杰
# @Python  : 3.7.5
# @File    : app
# @Project : search_images
import base64
import os
import uuid

from flask import Flask, render_template, request
from store import Store

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = Store(model_name='vgg16')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    image_base64 = request.form.get("image_search").split(';base64,')[1]
    image_format = request.form.get("image_search").split(
        ';base64,')[0].split('data:image/')[1]
    image_id = uuid.uuid4()
    # print(request.form.get("image_search"))
    # 保存文件到服务器本地
    image_path = f'{BASE_DIR}/static/search/{image_id}.{image_format}'
    with open(image_path, 'wb') as f:
        f.write(base64.b64decode(image_base64))
    result = db.search(image_path)
    result['type'] = 'success'
    return result


if __name__ == '__main__':
    app.run(debug=True)
