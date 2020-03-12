
#coding:utf8


import scrapy

class ImporteddrugItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    registration_number = scrapy.Field() # 注册证号
    product_type = scrapy.Field()  # 产品类别 
    dosage  = scrapy.Field()#剂型   索
    goods_chinese_name = scrapy.Field()#商品名（中文） 
    goods_english_name = scrapy.Field()#商品名（英文） 
    english_name = scrapy.Field()#产品名称（英文）    索
    chinese_name = scrapy.Field()#产品名称（中文） 
    medicine_benwei_code = scrapy.Field()#药品本位码    索
    company_chinese_name = scrapy.Field()#公司名称（中文） 
    company_english_name = scrapy.Field()#公司名称（英文） 
    nation_chinese_name =scrapy.Field()#国家/地区（中文） 
    nation_english_name = scrapy.Field()#国家/地区（英文）    索
    producer_chinese_name = scrapy.Field()#生产厂商（中文） 
    producer_english_name = scrapy.Field()#生产厂商（英文） 
    producer_nation_chinese_name =scrapy.Field()#厂商国家/地区（中文） 
    producer_nation_english_name = scrapy.Field()#厂商国家/地区（英文） 
    limited_date = scrapy.Field()#有效期截止日 
    certificated_issue_date = scrapy.Field()#发证日期