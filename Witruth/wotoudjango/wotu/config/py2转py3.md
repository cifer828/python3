## python2.7 to python3.5

## 环境ubuntu

## 1、安装python3.5

**sudo apt-get install python3.5

## 2、安装pip3

**sudo apt-get install python3-pip

## 3、安装第三方包

** pip3 install packageName

**项目依赖库

django
requests
lxml
pymysql
chardet
textrank4zh
pymongo
pandas
scrapy
sklearn
scipy
lda
gensim
xlwt
selenium

## 4、python2 转python3

** 利用python自带工具2to3.py

path：\Python27\Tools\Scripts\2to3.py

进入2to3.py所在目录内，执行

2to3.py -w dir

dir为需要转换的py2文件或目录

转换后会自动备份原py2文件为.bak

注：注释内代码不会转换