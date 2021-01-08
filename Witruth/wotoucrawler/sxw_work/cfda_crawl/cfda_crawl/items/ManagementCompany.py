
#coding:utf8


import scrapy

class ManagementCompanyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    mc_certif_num = scrapy.Field()  # 证号    索
    mc_name = scrapy.Field()#企业名称 
    mc_pos = scrapy.Field()#注册地址 
    mc_stoc_pos= scrapy.Field()#仓库地址 
    mc_lagal_rep = scrapy.Field()#法定代表人 
    mc_law_manager = scrapy.Field()#企业负责人 
    mc_qua_manager = scrapy.Field()#质量负责人 
    mc_manage_style = scrapy.Field()#经营方式 
    mc_manage_scope = scrapy.Field()#经营范围 
    mc_certif_issue_date = scrapy.Field()#发证日期 
    mc_limit_date = scrapy.Field()#有效期至 
    mc_issue_department = scrapy.Field()#发证部门