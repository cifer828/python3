
#coding:utf8


import scrapy

class DrugprotectionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    produce_com = scrapy.Field()  # 编号    索
    medicine_name = scrapy.Field()#名称 
    permit_num = scrapy.Field()#批准文号 
    protect_degree = scrapy.Field()#保护级别 
    protect_start_date = scrapy.Field()#保护起始日 
    protect_end_date = scrapy.Field()#保护终止日    索
    medicine_production_company = scrapy.Field()#生产企业 
    dosage  = scrapy.Field()#剂型 
    limited_date = scrapy.Field()#保护期限