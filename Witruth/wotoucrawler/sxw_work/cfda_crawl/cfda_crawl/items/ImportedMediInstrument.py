
#coding:utf8


import scrapy

class ImportedMediInstrumentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    #索
    imi_product_name = scrapy.Field()  # 产品名称 
    imi_register_num = scrapy.Field()#编号     索
    imi_register_per_name = scrapy.Field()#注册人名称 
    imi_register_per_address = scrapy.Field()#注册人地址 
    imi_production_pos = scrapy.Field()#生产地址 
    imi_agent_per_name = scrapy.Field()#代理人名称 
    imi_agent_per_address = scrapy.Field()#代理人地址 
    imi_type_spec_name = scrapy.Field()#型号与规格     索
    imi_stru = scrapy.Field()#结构及组成 
    imi_application_range = scrapy.Field()#适用范围 
    imi_produce_english_name = scrapy.Field()#生产国 
    imi_permit_date = scrapy.Field()#批准日期 
    imi_limit_date = scrapy.Field()#有效期至    索
    imi_producer_chinese_name = scrapy.Field()#生产商中文名 
    imi_product_chinese_name = scrapy.Field()#产品名称中文名 
    imi_product_standard = scrapy.Field()#产品标准 
    imi_produce_nation_chinese_name = scrapy.Field()#生产国中文名 
    imi_services = scrapy.Field()#售后服务机构    索
    imi_ingredient = scrapy.Field()#主要组成成分 
    imi_expect_usage = scrapy.Field()#预期用途 
    imi_save_condition =scrapy.Field()#产品储存条件和有效期 
    imi_apprve_org = scrapy.Field()#审批部门 
    imi_change_info = scrapy.Field()#变更情况