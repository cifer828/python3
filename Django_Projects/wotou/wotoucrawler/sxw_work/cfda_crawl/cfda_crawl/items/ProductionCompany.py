
#coding:utf8


import scrapy

class ProductionCompanyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    pc_name = scrapy.Field()
    pc_code = scrapy.Field()  # 编号    索
    pc_org_code = scrapy.Field()#组织机构码 
    pc_class_num = scrapy.Field()#分类码 
    pc_position = scrapy.Field()#省市 
    pc_com_name = scrapy.Field()#注册地址 
    pc_pro_pos = scrapy.Field()#生产地址 
    pc_cer_issue_date = scrapy.Field()#发证日期 
    pc_limit_date = scrapy.Field()#有效日期 
    pc_cer_issue_org = scrapy.Field()#发证机关 
    pc_cer_issue_per = scrapy.Field()#签发人 
    pc_supervision_org = scrapy.Field()#日常监督机构 