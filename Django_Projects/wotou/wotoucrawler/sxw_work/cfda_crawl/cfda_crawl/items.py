# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DomesticdrugItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    type=scrapy.Field()
    permit_num = scrapy.Field()  #批准文号
    english_name = scrapy.Field()
    chinese_name = scrapy.Field()
    dosage  = scrapy.Field() #剂型
    produce_com = scrapy.Field()
    product_type = scrapy.Field()
    medicine_benwei_code = scrapy.Field()#药品本位码
    approval_date=scrapy.Field()

class ChineseMediInstrumentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    type = scrapy.Field()
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


class DomesticdruggoodsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    type = scrapy.Field()
    permit_num = scrapy.Field()  #批准文号
    english_name = scrapy.Field()
    chinese_name = scrapy.Field()
    goods_name=scrapy.Field()
    dosage  = scrapy.Field() #剂型
    produce_com = scrapy.Field()
    product_type = scrapy.Field()
    medicine_benwei_code = scrapy.Field()#药品本位码
    approval_date=scrapy.Field()


class DrugprotectionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    type = scrapy.Field()
    produce_com = scrapy.Field()  # 编号    索
    medicine_name = scrapy.Field()#名称 
    permit_num = scrapy.Field()#批准文号 
    protect_degree = scrapy.Field()#保护级别 
    protect_start_date = scrapy.Field()#保护起始日 
    protect_end_date = scrapy.Field()#保护终止日    索
    medicine_production_company = scrapy.Field()#生产企业 
    dosage  = scrapy.Field()#剂型 
    limited_date = scrapy.Field()#保护期限



class ImporteddrugItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    type = scrapy.Field()
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


class ImporteddruggoodsItem(scrapy.Item):
    type = scrapy.Field()
    registration_number = scrapy.Field()  # 注册证号
    product_type = scrapy.Field()  # 产品类别 
    dosage  = scrapy.Field()#剂型   索
    goods_chinese_name = scrapy.Field()#商品名（中文） 
    goods_english_name = scrapy.Field()#商品名（英文） 
    english_name = scrapy.Field()#产品名称（英文）    索
    chinese_name = scrapy.Field()#产品名称（中文）    索
    company_chinese_name = scrapy.Field()#公司名称（中文） 
    company_english_name = scrapy.Field()#公司名称（英文） 
    nation_chinese_name = scrapy.Field()#国家/地区（中文） 
    nation_english_name =scrapy.Field()#国家/地区（英文）    索
    producer_chinese_name = scrapy.Field()#生产厂商（中文） 
    producer_english_name = scrapy.Field()#生产厂商（英文） 
    producer_nation_chinese_name = scrapy.Field()#厂商国家/地区（中文） 
    producer_nation_english_name = scrapy.Field()#厂商国家/地区（英文） 
    limited_date = scrapy.Field()#有效期截止日 
    certificated_issue_date = scrapy.Field()#发证日期


class ImportedMediInstrumentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    #索
    type = scrapy.Field()
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


class ManagementCompanyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    type = scrapy.Field()
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


class MediInstrumentRecordsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    type = scrapy.Field()
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


class ProductionCompanyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #medicine_type = scrapy.item()   #药品类型标识，0-国产药品，1-国产药品商品
    type = scrapy.Field()
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


