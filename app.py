#!/usr/bin/env python
# @Time    : 2020/5/10 12:55
# @Author  : 洪英杰
# @Python  : 3.7.5
# @File    : app
# @Project : search_images
import base64
import uuid

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    image = request.form.get("image_search").split('base64,')[1]
    image_id = uuid.uuid4()
    # print(image)
    # 保存文件到服务器本地
    with open(f'static/search/{image_id}.jpg', 'wb') as f:
        f.write(base64.b64decode(image))
    return {}


if __name__ == '__main__':
    app.run(debug=True)
