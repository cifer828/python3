# coding: UTF-8
import base64
import os

with open('test.txt', 'r') as f:
    path = f.read()
with open(path, 'rb') as f:
    imgData = base64.b64encode(f.read())
    print(imgData[:10])