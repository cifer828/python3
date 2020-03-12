
#coding:utf8


import scrapy

class DomesticdrugItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    permit_num = scrapy.Field()  #批准文号
    english_name = scrapy.Field()
    chinese_name = scrapy.Field()
    dosage  = scrapy.Field() #剂型
    produce_com = scrapy.Field()
    product_type = scrapy.Field()
    medicine_benwei_code = scrapy.Field()#药品本位码
    approval_date=scrapy.Field()