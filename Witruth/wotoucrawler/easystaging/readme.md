- http://www.qichacha.com/search?key={key}
- http://www.qiduowei.com/search?key={key}
- http://www.xizhi.com/search?wd={key}
- *http://www.tianyancha.com/search/{key}*
- *http://www.qixin.com/search?key={key}*

## 1 [overview](http://doc.scrapy.org/en/1.1/intro/overview.html)

## 2 [使用Scrapy抓取数据步骤](http://blog.javachen.com/2014/05/24/using-scrapy-to-cralw-data.html)

### 2.1 创建工程结构

`scrapy startproject easystaging`

### 2.2 spawn一个爬虫

`scrapy genspider {spider name: qichacha|qiduowei|xizhi} {domain.com}`

### 2.3 [调试选择器:xpath,css](http://www.pycoding.com/2016/03/14/scrapy-04.html)

请结合`scrapy shell`和`chrome的调试工具生成的xpath`**在本地做调试**

`scrapy shell {URL}`

### 2.4 运行
-  首先给定爬虫需要的输入文件，input.txt是查询公司基本信息用到的，zhuanli_input.txt 是查询专利信息用到的，格式：一行一个公司名
-  其次运行 scrapy crawl {spider name} 即可得到对应结果的excel文件
- `scrapy crawl {spider name: qichacha|qiduowei|xizhi}`

- `scrapy runspider ./easystaging/spiders/{XXSPIDER}.py # -o a.out.json`
