
#coding:utf8


import scrapy

class ChineseMediInstrumentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    cmi_register_num = scrapy.Field() # 编号     索
    cmi_register_per_name = scrapy.Field()#注册人名称 
    cmi_register_per_address =scrapy.Field()#注册人地址     索
    cmi_name = scrapy.Field()#产品名称 
    cmi_type_spec_name = scrapy.Field()#型号与规格     索
    cmi_stru = scrapy.Field()#结构及组成 
    cmi_application_range = scrapy.Field()#适用范围 
    cmi_permit_date = scrapy.Field()#批准日期 
    cmi_limit_date = scrapy.Field()#有效期至 
    cmi_product_standard = scrapy.Field()#产品标准     索
    cmi_ingredient = scrapy.Field()#主要组成成分 
    cmi_expect_usage =scrapy.Field()#预期用途 
    cmi_save_condition = scrapy.Field()#产品储存条件和有效期 
    cmi_apprve_org = scrapy.Field()#审批部门 
    cmi_change_info = scrapy.Field()#变更情况