
#coding:utf8


import scrapy

class MediInstrumentRecordsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    mir_num = scrapy.Field()  # 备案号 
    mir_medicine_type = scrapy.Field()#产品类别    索
    mir_record_name = scrapy.Field()#备案人名称    索
    mir_record_org = scrapy.Field()#备案人组织机构代码 
    mir_record_register_address = scrapy.Field()#备案人注册地址 
    mir_produce_pos = scrapy.Field()#生产地址    索
    mir_production_name = scrapy.Field()#产品名称 
    #mir_production_class_name =scrapy.Field()#产品分类名称 
    mir_type_spec_name = scrapy.Field()#型号与规格 
    mir_limit_date = scrapy.Field()#有效期至    索
    mir_ingredient = scrapy.Field()#主要组成成分 
    mir_application_expection = scrapy.Field()#预期范围 
    mir_note = scrapy.Field()#备注 
    mir_record_depart = scrapy.Field()#备案单位 
    mir_record_date = scrapy.Field()#备案日期 
    mir_change_situation = scrapy.Field()#变更情况 
    mir_record_status =scrapy.Field()#备案状态