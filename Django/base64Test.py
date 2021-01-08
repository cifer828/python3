# -*- coding: utf-8 -*
import base64
import re
with open(unicode('photos/轨道试验线.jpg','utf8'),'rb') as f:
    imgData = base64.b64encode(f.read())
print imgData
# with open('23.txt') as f:
#     imgData2 = f.read()
# img = base64.b64decode(imgData)
# img2 = base64.b64decode(re.findall(',(.*)',imgData2)[0])
# print img
# with open('photo2.txt', 'w') as f:
#     f.write(imgData)
# with open('photos/轨道试验线.jpg'.encode(), 'wb') as f:
#     f.write(img2)